class ServerConfig:
    def __init__(self, id: str, name: str, command: str, 
                 arguments: list, env_vars: dict, working_dir: str = ""):
        self.id = id
        self.name = name
        self.command = command
        self.arguments = arguments
        self.env_vars = env_vars
        self.working_dir = working_dir
        self.status = "offline"  # offline, starting, online, error
        
    def to_dict(self) -> dict:
        """Serialize configuration to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "command": self.command,
            "arguments": self.arguments,
            "env_vars": self.env_vars,
            "working_dir": self.working_dir,
            "status": self.status
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ServerConfig':
        """Create configuration from dictionary"""
        return cls(
            id=data["id"],
            name=data["name"],
            command=data["command"],
            arguments=data["arguments"],
            env_vars=data["env_vars"],
            working_dir=data.get("working_dir", "")
        )