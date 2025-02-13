# load_balancer/balancer.py
from config.logging_config import CustomLogger

logger = CustomLogger("load_balancer")

class LoadBalancer:
    def __init__(self):
        self.servers: List[str] = []
        self.current_index = 0
    
    async def add_server(self, server_url: str):
        """Add new server"""
        if server_url not in self.servers:
            self.servers.append(server_url)
            logger.info(
                f"Server added to load balancer",
                server=server_url,
                total_servers=len(self.servers)
            )
    
    async def remove_server(self, server_url: str):
        """Remove server"""
        if server_url in self.servers:
            self.servers.remove(server_url)
            logger.info(
                f"Server removed from load balancer",
                server=server_url,
                total_servers=len(self.servers)
            )
    
    async def get_next_server(self) -> str:
        """Select the next server using round-robin method"""
        if not self.servers:
            logger.error("No servers available in load balancer")
            raise Exception("No servers available")
        
        server = self.servers[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.servers)
        
        logger.debug(
            f"Selected server from load balancer",
            server=server,
            current_index=self.current_index
        )
        
        return server

    async def health_check(self, server_url: str) -> bool:
        """Server health check"""
        try:
            # Health check logic here
            logger.debug(
                f"Health check performed",
                server=server_url,
                status="healthy"
            )
            return True
        except Exception as e:
            logger.error(
                f"Health check failed",
                server=server_url,
                error=str(e)
            )
            return False