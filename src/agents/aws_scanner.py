"""AWS Scanner Agent - Scans AWS infrastructure and maps to system designs"""

import json
import subprocess
from typing import Optional, Dict, List, Tuple
from rich.console import Console
from rich.prompt import Prompt, Confirm

from agents.design_recommender import SystemComponent, Connection, SystemDesign

console = Console()


class AwsScannerAgent:
    """AI Agent that scans AWS infrastructure using AWS CLI and maps to SystemDesign"""
    
    def __init__(self, region: Optional[str] = None):
        """
        Initialize the AWS Scanner Agent
        
        Args:
            region: AWS region to scan (defaults to configured default region)
        """
        self.region = region
        self.discovered_resources = {
            "ec2_instances": [],
            "rds_instances": [],
            "lambda_functions": [],
            "s3_buckets": [],
            "load_balancers": [],
            "sqs_queues": [],
            "elasticache_clusters": [],
            "api_gateways": [],
            "ecs_services": [],
            "security_groups": []
        }
        
    def check_aws_cli_installed(self) -> bool:
        """Check if AWS CLI is installed"""
        try:
            result = subprocess.run(
                ["aws", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def check_aws_authentication(self) -> Tuple[bool, Optional[Dict]]:
        """
        Check if user is authenticated with AWS
        
        Returns:
            Tuple of (is_authenticated, identity_info)
        """
        try:
            result = subprocess.run(
                ["aws", "sts", "get-caller-identity"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                identity = json.loads(result.stdout)
                return True, identity
            else:
                return False, None
                
        except (subprocess.SubprocessError, json.JSONDecodeError):
            return False, None
    
    def guide_aws_authentication(self) -> bool:
        """
        Guide user through AWS authentication process
        
        Returns:
            True if authentication successful, False otherwise
        """
        console.print("\n[yellow]⚠️  You need to authenticate with AWS first.[/yellow]\n")
        console.print("You have two main options:\n")
        console.print("1. [bold]AWS Configure[/bold] - For IAM user credentials")
        console.print("   Run: [cyan]aws configure[/cyan]")
        console.print("   You'll need: Access Key ID, Secret Access Key, Region\n")
        console.print("2. [bold]AWS SSO[/bold] - For AWS SSO users")
        console.print("   Run: [cyan]aws sso login[/cyan]")
        console.print("   (Note: You must have SSO configured first)\n")
        
        auth_method = Prompt.ask(
            "Which authentication method?",
            choices=["configure", "sso", "skip"],
            default="configure"
        )
        
        if auth_method == "skip":
            return False
        
        if auth_method == "configure":
            console.print("\n[cyan]Please run this command in your terminal:[/cyan]")
            console.print("[bold]aws configure[/bold]\n")
        else:  # sso
            console.print("\n[cyan]Please run this command in your terminal:[/cyan]")
            console.print("[bold]aws sso login[/bold]\n")
        
        console.print("After you've authenticated, press Enter to continue...")
        input()
        
        # Re-check authentication
        is_auth, identity = self.check_aws_authentication()
        if is_auth:
            console.print(f"[green]✓ Successfully authenticated as: {identity.get('Arn', 'Unknown')}[/green]")
            return True
        else:
            console.print("[red]✗ Authentication failed. Please try again manually.[/red]")
            return False
    
    def run_aws_command(self, command: List[str]) -> Optional[Dict]:
        """
        Execute an AWS CLI command and return parsed JSON output
        
        Args:
            command: List of command parts (e.g., ["aws", "ec2", "describe-instances"])
            
        Returns:
            Parsed JSON response or None on error
        """
        try:
            # Add region if specified
            if self.region:
                command.extend(["--region", self.region])
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout:
                return json.loads(result.stdout)
            else:
                # Silently handle permission errors and empty responses
                return None
                
        except (subprocess.SubprocessError, json.JSONDecodeError, subprocess.TimeoutExpired):
            return None
    
    def discover_ec2_instances(self):
        """Discover EC2 instances"""
        console.print("[cyan]  • Scanning EC2 instances...[/cyan]")
        response = self.run_aws_command(["aws", "ec2", "describe-instances"])
        
        if response and "Reservations" in response:
            for reservation in response["Reservations"]:
                for instance in reservation.get("Instances", []):
                    instance_id = instance.get("InstanceId", "Unknown")
                    instance_type = instance.get("InstanceType", "Unknown")
                    state = instance.get("State", {}).get("Name", "unknown")
                    
                    # Get name from tags
                    name = instance_id
                    for tag in instance.get("Tags", []):
                        if tag.get("Key") == "Name":
                            name = tag.get("Value", instance_id)
                            break
                    
                    if state == "running":
                        self.discovered_resources["ec2_instances"].append({
                            "id": instance_id,
                            "name": name,
                            "type": instance_type,
                            "vpc_id": instance.get("VpcId"),
                            "security_groups": [sg["GroupId"] for sg in instance.get("SecurityGroups", [])]
                        })
    
    def discover_rds_instances(self):
        """Discover RDS database instances"""
        console.print("[cyan]  • Scanning RDS databases...[/cyan]")
        response = self.run_aws_command(["aws", "rds", "describe-db-instances"])
        
        if response and "DBInstances" in response:
            for db in response["DBInstances"]:
                self.discovered_resources["rds_instances"].append({
                    "id": db.get("DBInstanceIdentifier", "Unknown"),
                    "name": db.get("DBInstanceIdentifier", "Unknown"),
                    "engine": db.get("Engine", "unknown"),
                    "status": db.get("DBInstanceStatus", "unknown")
                })
    
    def discover_lambda_functions(self):
        """Discover Lambda functions"""
        console.print("[cyan]  • Scanning Lambda functions...[/cyan]")
        response = self.run_aws_command(["aws", "lambda", "list-functions"])
        
        if response and "Functions" in response:
            for func in response["Functions"]:
                self.discovered_resources["lambda_functions"].append({
                    "name": func.get("FunctionName", "Unknown"),
                    "runtime": func.get("Runtime", "unknown"),
                    "handler": func.get("Handler", "unknown")
                })
    
    def discover_s3_buckets(self):
        """Discover S3 buckets"""
        console.print("[cyan]  • Scanning S3 buckets...[/cyan]")
        response = self.run_aws_command(["aws", "s3api", "list-buckets"])
        
        if response and "Buckets" in response:
            for bucket in response["Buckets"]:
                self.discovered_resources["s3_buckets"].append({
                    "name": bucket.get("Name", "Unknown")
                })
    
    def discover_load_balancers(self):
        """Discover Application and Network Load Balancers"""
        console.print("[cyan]  • Scanning Load Balancers...[/cyan]")
        response = self.run_aws_command(["aws", "elbv2", "describe-load-balancers"])
        
        if response and "LoadBalancers" in response:
            for lb in response["LoadBalancers"]:
                self.discovered_resources["load_balancers"].append({
                    "name": lb.get("LoadBalancerName", "Unknown"),
                    "type": lb.get("Type", "unknown"),
                    "scheme": lb.get("Scheme", "unknown")
                })
    
    def discover_sqs_queues(self):
        """Discover SQS queues"""
        console.print("[cyan]  • Scanning SQS queues...[/cyan]")
        response = self.run_aws_command(["aws", "sqs", "list-queues"])
        
        if response and "QueueUrls" in response:
            for queue_url in response["QueueUrls"]:
                # Extract queue name from URL
                queue_name = queue_url.split("/")[-1]
                self.discovered_resources["sqs_queues"].append({
                    "name": queue_name,
                    "url": queue_url
                })
    
    def discover_elasticache_clusters(self):
        """Discover ElastiCache clusters"""
        console.print("[cyan]  • Scanning ElastiCache clusters...[/cyan]")
        response = self.run_aws_command(["aws", "elasticache", "describe-cache-clusters"])
        
        if response and "CacheClusters" in response:
            for cluster in response["CacheClusters"]:
                self.discovered_resources["elasticache_clusters"].append({
                    "id": cluster.get("CacheClusterId", "Unknown"),
                    "engine": cluster.get("Engine", "unknown"),
                    "status": cluster.get("CacheClusterStatus", "unknown")
                })
    
    def discover_api_gateways(self):
        """Discover API Gateway REST APIs"""
        console.print("[cyan]  • Scanning API Gateways...[/cyan]")
        response = self.run_aws_command(["aws", "apigateway", "get-rest-apis"])
        
        if response and "items" in response:
            for api in response["items"]:
                self.discovered_resources["api_gateways"].append({
                    "id": api.get("id", "Unknown"),
                    "name": api.get("name", "Unknown"),
                    "description": api.get("description", "")
                })
    
    def discover_ecs_services(self):
        """Discover ECS services"""
        console.print("[cyan]  • Scanning ECS services...[/cyan]")
        
        # First, list clusters
        clusters_response = self.run_aws_command(["aws", "ecs", "list-clusters"])
        
        if clusters_response and "clusterArns" in clusters_response:
            for cluster_arn in clusters_response["clusterArns"]:
                cluster_name = cluster_arn.split("/")[-1]
                
                # List services in this cluster
                services_response = self.run_aws_command([
                    "aws", "ecs", "list-services",
                    "--cluster", cluster_name
                ])
                
                if services_response and "serviceArns" in services_response:
                    for service_arn in services_response["serviceArns"]:
                        service_name = service_arn.split("/")[-1]
                        self.discovered_resources["ecs_services"].append({
                            "name": service_name,
                            "cluster": cluster_name
                        })
    
    def scan_aws_infrastructure(self) -> bool:
        """
        Main method to scan AWS infrastructure
        
        Returns:
            True if scan successful, False otherwise
        """
        # Check AWS CLI installation
        if not self.check_aws_cli_installed():
            console.print("[red]✗ AWS CLI is not installed.[/red]")
            console.print("Please install it from: https://aws.amazon.com/cli/")
            return False
        
        console.print("[green]✓ AWS CLI is installed[/green]")
        
        # Check authentication
        is_auth, identity = self.check_aws_authentication()
        
        if not is_auth:
            if not self.guide_aws_authentication():
                return False
            # Re-check after guided auth
            is_auth, identity = self.check_aws_authentication()
            if not is_auth:
                return False
        else:
            console.print(f"[green]✓ Authenticated as: {identity.get('Arn', 'Unknown')}[/green]")
        
        # Get region
        if not self.region:
            result = subprocess.run(
                ["aws", "configure", "get", "region"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                self.region = result.stdout.strip()
            else:
                self.region = Prompt.ask("Enter AWS region to scan", default="us-east-1")
        
        console.print(f"[cyan]Scanning AWS region: {self.region}[/cyan]\n")
        
        # Discover all resources
        self.discover_ec2_instances()
        self.discover_rds_instances()
        self.discover_lambda_functions()
        self.discover_s3_buckets()
        self.discover_load_balancers()
        self.discover_sqs_queues()
        self.discover_elasticache_clusters()
        self.discover_api_gateways()
        self.discover_ecs_services()
        
        console.print("[green]✓ AWS infrastructure scan complete[/green]\n")
        return True
    
    def infer_connections(self, components: List[SystemComponent]) -> List[Connection]:
        """
        Infer connections between components based on common patterns
        
        Args:
            components: List of discovered components
            
        Returns:
            List of inferred connections
        """
        connections = []
        component_map = {comp.name: comp for comp in components}
        
        # Pattern 1: Load Balancers connect to EC2/ECS
        lb_components = [c for c in components if c.type == "load_balancer"]
        ec2_components = [c for c in components if c.type in ["service", "compute"]]
        
        for lb in lb_components:
            for ec2 in ec2_components:
                connections.append(Connection(
                    from_component=lb.name,
                    to_component=ec2.name,
                    connection_type="http",
                    description="Load balancer distributes traffic to service"
                ))
        
        # Pattern 2: Services connect to databases
        service_components = [c for c in components if c.type in ["service", "compute", "function"]]
        db_components = [c for c in components if c.type == "database"]
        
        for service in service_components:
            for db in db_components:
                connections.append(Connection(
                    from_component=service.name,
                    to_component=db.name,
                    connection_type="sync",
                    description="Service reads/writes data to database"
                ))
        
        # Pattern 3: Services connect to cache
        cache_components = [c for c in components if c.type == "cache"]
        
        for service in service_components:
            for cache in cache_components:
                connections.append(Connection(
                    from_component=service.name,
                    to_component=cache.name,
                    connection_type="sync",
                    description="Service uses cache for performance"
                ))
        
        # Pattern 4: Services/Lambda connect to queues
        queue_components = [c for c in components if c.type == "queue"]
        
        for service in service_components:
            for queue in queue_components:
                connections.append(Connection(
                    from_component=service.name,
                    to_component=queue.name,
                    connection_type="async",
                    description="Service publishes messages to queue"
                ))
        
        # Pattern 5: API Gateway connects to Lambda
        api_components = [c for c in components if c.type == "api"]
        lambda_components = [c for c in components if "Lambda" in c.name or c.type == "function"]
        
        for api in api_components:
            for lambda_func in lambda_components:
                connections.append(Connection(
                    from_component=api.name,
                    to_component=lambda_func.name,
                    connection_type="http",
                    description="API Gateway routes requests to Lambda function"
                ))
        
        # Pattern 6: Services use S3 storage
        storage_components = [c for c in components if c.type == "storage"]
        
        for service in service_components[:1]:  # Only connect first service to avoid clutter
            for storage in storage_components[:1]:  # Only first storage
                connections.append(Connection(
                    from_component=service.name,
                    to_component=storage.name,
                    connection_type="sync",
                    description="Service stores/retrieves files from storage"
                ))
        
        return connections
    
    def convert_to_system_design(self) -> SystemDesign:
        """
        Convert discovered AWS resources to SystemDesign format
        
        Returns:
            SystemDesign object compatible with ASCII Artist Agent
        """
        components = []
        
        # Convert EC2 instances
        for ec2 in self.discovered_resources["ec2_instances"]:
            components.append(SystemComponent(
                name=ec2["name"],
                type="service",
                description=f"EC2 Instance ({ec2['type']})"
            ))
        
        # Convert RDS instances
        for rds in self.discovered_resources["rds_instances"]:
            components.append(SystemComponent(
                name=rds["name"],
                type="database",
                description=f"{rds['engine'].upper()} Database"
            ))
        
        # Convert Lambda functions
        for lambda_func in self.discovered_resources["lambda_functions"]:
            components.append(SystemComponent(
                name=lambda_func["name"],
                type="function",
                description=f"Lambda Function ({lambda_func['runtime']})"
            ))
        
        # Convert S3 buckets
        for s3 in self.discovered_resources["s3_buckets"]:
            components.append(SystemComponent(
                name=s3["name"],
                type="storage",
                description="S3 Bucket for object storage"
            ))
        
        # Convert Load Balancers
        for lb in self.discovered_resources["load_balancers"]:
            components.append(SystemComponent(
                name=lb["name"],
                type="load_balancer",
                description=f"{lb['type'].upper()} ({lb['scheme']})"
            ))
        
        # Convert SQS queues
        for sqs in self.discovered_resources["sqs_queues"]:
            components.append(SystemComponent(
                name=sqs["name"],
                type="queue",
                description="SQS Message Queue"
            ))
        
        # Convert ElastiCache clusters
        for cache in self.discovered_resources["elasticache_clusters"]:
            components.append(SystemComponent(
                name=cache["id"],
                type="cache",
                description=f"ElastiCache ({cache['engine'].capitalize()})"
            ))
        
        # Convert API Gateways
        for api in self.discovered_resources["api_gateways"]:
            components.append(SystemComponent(
                name=api["name"],
                type="api",
                description=f"API Gateway - {api.get('description', 'REST API')}"
            ))
        
        # Convert ECS services
        for ecs in self.discovered_resources["ecs_services"]:
            components.append(SystemComponent(
                name=ecs["name"],
                type="service",
                description=f"ECS Service (Cluster: {ecs['cluster']})"
            ))
        
        # Infer connections
        connections = self.infer_connections(components)
        
        # Create notes
        notes = [
            f"Scanned AWS region: {self.region}",
            f"Total resources discovered: {len(components)}",
            "Connections are inferred based on common AWS architecture patterns"
        ]
        
        # Create title and description
        resource_counts = {
            "EC2": len(self.discovered_resources["ec2_instances"]),
            "RDS": len(self.discovered_resources["rds_instances"]),
            "Lambda": len(self.discovered_resources["lambda_functions"]),
            "S3": len(self.discovered_resources["s3_buckets"]),
            "Load Balancers": len(self.discovered_resources["load_balancers"]),
            "SQS": len(self.discovered_resources["sqs_queues"]),
            "ElastiCache": len(self.discovered_resources["elasticache_clusters"]),
            "API Gateway": len(self.discovered_resources["api_gateways"]),
            "ECS": len(self.discovered_resources["ecs_services"])
        }
        
        resource_summary = ", ".join([f"{count} {name}" for name, count in resource_counts.items() if count > 0])
        
        return SystemDesign(
            title=f"AWS Infrastructure - {self.region}",
            description=f"Automatically discovered AWS architecture containing: {resource_summary}",
            components=components,
            connections=connections,
            notes=notes
        )
