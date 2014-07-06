class AgentCollections():
    Agents = 'agents'
    Hardware = 'hardware_per_agent'


class AgentKeys():
    Id = 'id'
    AgentId = 'agent_id'
    ComputerName = 'computer_name'
    DisplayName = 'display_name'
    HostName = 'host_name'
    OsCode = 'os_code'
    OsString = 'os_string'
    Views = 'views'
    NeedsReboot = 'needs_reboot'
    AgentStatus = 'agent_status'
    BasicStats = 'basic_stats'
    Environment = 'environment'
    SystemInfo = 'system_info'
    Hardware = 'hardware'
    Tags = 'tags'
    MachineType = 'machine_type'
    LastAgentUpdate = 'last_agent_update'
    DateAdded = 'date_added'
    Plugins = 'plugins'
    Core = 'core'
    Rebooted = 'rebooted'
    BitType = 'bit_type'
    Version = 'version'
    Token = 'token'
    Enabled = 'enabled'
    AssignNewToken = 'assign_new_token'


class AgentIndexes():
    Views = 'views'
    OsCode = 'os_code'


class HardwarePerAgentKeys():
    Id = 'id'
    AgentId = 'agent_id'
    Name = 'name'
    Type = 'type'
    Nic = 'nic'
    Mac = 'mac'
    IpAddress = 'ip_address'
    CreatedBy = 'created_by'
    AddedBy = 'added_by'
    SpeedMhz = 'speed_mhz'
    BitType = 'bit_type'
    CpuId = 'cpu_id'
    CacheKb = 'cache_kb'
    Cores = 'cores'
    FileSystem = 'file_system'
    SizeKb = 'size_kb'
    FreeSizeKb = 'free_size_kb'
    Core = 'core'
    TotalMemory = 'total_memory'
    RamKb = 'ram_kb'


class HardwarePerAgentIndexes():
    AgentId = 'agent_id'
    Type = 'type'
    AgentIdAndType = 'agent_id_and_type'
