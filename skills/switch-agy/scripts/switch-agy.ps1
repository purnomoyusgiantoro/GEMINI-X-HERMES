param(
    [string]$Action = "",
    [string]$Target = ""
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
python "$scriptDir\switch-agy-core.py" $Action $Target
