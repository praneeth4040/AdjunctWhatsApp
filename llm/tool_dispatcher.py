from tools.reminder import set_reminder

def dispatch_tool_call(name, args, recipient):
    """
    Dispatches the tool call to the correct function based on name.
    Args:
        name (str): The name of the function/tool to call.
        args (dict): Arguments for the function.
    Returns:
        dict: The result from the tool function.
    """
    if name == "set_reminder":
        return set_reminder(recipient,args["event"], args["time_str"])
    else:
        return {"result": f"Unknown tool: {name}"} 