#Requires -Version 5.1
<#
.SYNOPSIS
  Corrected AWS CLI workflow for PITER AiOps Bedrock KB, Lambdas, and agent deploy.

.DESCRIPTION
  Fixes the failures seen in manual terminal runs:
  - KB data source prefix pointed at deleted sample_documents/
  - Missing piter-* Lambdas (iiq-* were deleted first)
  - PowerShell ARN interpolation for lambda add-permission
  - Agent rename with spaces (use existing agent name)
  - create-agent-version / invoke-agent (not in AWS CLI — use alias update + Python)
#>
param(
    [string]$AwsProfile = "reemmor",
    [string]$AwsRegion = "us-east-1",
    [string]$Bucket = "reem-amdocs-ai-artifacts-3331",
    [string]$KbId = "RBTJM6NIG9",
    [string]$DataSourceId = "YICXAB6WOG",
    [string]$AgentId = "HH4YGSLZUE",
    [string]$AgentAliasId = "O2EM03R4R3",
    [string]$AccountId = "329597159579",
    [switch]$SkipAgentAlias
)

$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $false
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

$env:AWS_PROFILE = $AwsProfile
$env:AWS_REGION = $AwsRegion

# Bedrock KB IAM role currently grants s3:GetObject on sample_documents/, not knowledge_base/.
$KbPrefix = "projects/piter-aiops/data/sample_documents/"
$KbMirrorPrefix = "projects/piter-aiops/knowledge_base/"
$LambdaRole = "arn:aws:iam::${AccountId}:role/incidentiq-lambda-role"
$AgentSourceArn = "arn:aws:bedrock:${AwsRegion}:${AccountId}:agent/${AgentId}"

function Write-Step([string]$Message) {
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Copy-TreeNoCache([string]$Source, [string]$Destination) {
    New-Item -ItemType Directory -Force -Path $Destination | Out-Null
    Get-ChildItem -Path $Source -Recurse -File |
        Where-Object { $_.FullName -notmatch '\\__pycache__\\' -and $_.Extension -ne '.pyc' } |
        ForEach-Object {
            $relative = $_.FullName.Substring($Source.Length).TrimStart('\')
            $target = Join-Path $Destination $relative
            $targetDir = Split-Path $target -Parent
            if (-not (Test-Path $targetDir)) {
                New-Item -ItemType Directory -Force -Path $targetDir | Out-Null
            }
            Copy-Item $_.FullName $target -Force
        }
}

function New-ActionGroupZip([string]$Name) {
    $build = Join-Path $RepoRoot "dist/build-$Name"
    $zip = Join-Path $RepoRoot "dist/$Name.zip"
    if (Test-Path $build) { Remove-Item $build -Recurse -Force }
    New-Item -ItemType Directory -Force -Path $build | Out-Null

    Copy-Item "action_groups/lambda_root.py" $build
    Copy-Item "action_groups/$Name/lambda_function.py" $build
    Copy-TreeNoCache (Join-Path $RepoRoot "app") (Join-Path $build "app")
    Copy-TreeNoCache (Join-Path $RepoRoot "data") (Join-Path $build "data")

    if (Test-Path $zip) { Remove-Item $zip -Force }
    Compress-Archive -Path (Join-Path $build "*") -DestinationPath $zip -Force
    return $zip
}

function Invoke-Aws([string[]]$AwsArgs) {
    $prevEap = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    & aws @AwsArgs
    $exit = $LASTEXITCODE
    $ErrorActionPreference = $prevEap
    return $exit
}

function Test-LambdaExists([string]$Name) {
    $exit = Invoke-Aws @("lambda", "get-function", "--function-name", $Name)
    return $exit -eq 0
}

function Ensure-Lambda([string]$Name, [string]$Description) {
    $zip = New-ActionGroupZip $Name
    $exists = Test-LambdaExists $Name

    if ($exists) {
        if ((Invoke-Aws @("lambda", "update-function-code", "--function-name", $Name, "--zip-file", "fileb://$zip")) -ne 0) {
            throw "update-function-code failed for $Name"
        }
        Write-Host "Updated Lambda $Name"
    } else {
        $createExit = Invoke-Aws @(
            "lambda", "create-function",
            "--function-name", $Name,
            "--runtime", "python3.12",
            "--role", $LambdaRole,
            "--handler", "lambda_function.lambda_handler",
            "--architectures", "arm64",
            "--timeout", "15",
            "--memory-size", "256",
            "--description", $Description,
            "--zip-file", "fileb://$zip"
        )
        if ($createExit -ne 0) {
            if ((Invoke-Aws @("lambda", "update-function-code", "--function-name", $Name, "--zip-file", "fileb://$zip")) -ne 0) {
                throw "create-function failed for $Name"
            }
            Write-Host "Updated Lambda $Name (create reported conflict)"
        } else {
            Write-Host "Created Lambda $Name"
        }
    }

    $arn = & aws lambda get-function --function-name $Name --query Configuration.FunctionArn --output text
    if ($LASTEXITCODE -ne 0) { throw "get-function failed for $Name" }

    if ((Invoke-Aws @(
            "lambda", "add-permission",
            "--function-name", $Name,
            "--statement-id", "AllowBedrockAgentInvoke-$Name",
            "--action", "lambda:InvokeFunction",
            "--principal", "bedrock.amazonaws.com",
            "--source-arn", $AgentSourceArn
        )) -ne 0) {
        Write-Host "Permission already present or add-permission skipped for $Name"
    }
    return $arn
}

Write-Step "Sync knowledge_base markdown to S3 (IAM-allowed prefix)"
aws s3 sync ".\knowledge_base\" "s3://$Bucket/$KbPrefix" --exclude "*" --include "*.md" --delete
aws s3 sync ".\knowledge_base\" "s3://$Bucket/$KbMirrorPrefix" --exclude "*" --include "*.md"

Write-Step "Point KB data source at IAM-allowed S3 prefix"
$dataSourcePath = Join-Path $RepoRoot "dist/update-data-source.json"
$dataSourceJson = @"
{
  "knowledgeBaseId": "$KbId",
  "dataSourceId": "$DataSourceId",
  "name": "piter-aiops-knowledge-base-datasource",
  "dataSourceConfiguration": {
    "type": "S3",
    "s3Configuration": {
      "bucketArn": "arn:aws:s3:::$Bucket",
      "inclusionPrefixes": ["$KbPrefix"]
    }
  },
  "vectorIngestionConfiguration": {
    "chunkingConfiguration": {
      "chunkingStrategy": "FIXED_SIZE",
      "fixedSizeChunkingConfiguration": {
        "maxTokens": 500,
        "overlapPercentage": 15
      }
    }
  }
}
"@
[System.IO.File]::WriteAllText($dataSourcePath, $dataSourceJson)
aws bedrock-agent update-data-source --cli-input-json "file://$dataSourcePath"
if ($LASTEXITCODE -ne 0) { throw "update-data-source failed" }

Write-Step "Start KB ingestion"
$IngestionJobId = aws bedrock-agent start-ingestion-job `
    --knowledge-base-id $KbId `
    --data-source-id $DataSourceId `
    --query ingestionJob.ingestionJobId `
    --output text
Write-Host "Ingestion job: $IngestionJobId"

do {
    Start-Sleep -Seconds 5
    $status = aws bedrock-agent get-ingestion-job `
        --knowledge-base-id $KbId `
        --data-source-id $DataSourceId `
        --ingestion-job-id $IngestionJobId `
        --query ingestionJob.status `
        --output text
    Write-Host "Ingestion status: $status"
} while ($status -in @("STARTING", "IN_PROGRESS"))

$stats = aws bedrock-agent get-ingestion-job `
    --knowledge-base-id $KbId `
    --data-source-id $DataSourceId `
    --ingestion-job-id $IngestionJobId `
    --query ingestionJob.statistics `
    --output json
Write-Host $stats

Write-Step "Deploy PITER action-group Lambdas"
$lambdaDefs = @(
    @{ Name = "piter-recent-deployments"; Description = "PITER recent deployments correlation" },
    @{ Name = "piter-service-context"; Description = "PITER service ownership and business impact" },
    @{ Name = "piter-similar-incidents"; Description = "PITER similar historical incidents" },
    @{ Name = "piter-escalation"; Description = "PITER escalation preview/mock/gated-live notifications" }
)
$lambdaArns = @{}
foreach ($def in $lambdaDefs) {
    $lambdaArns[$def.Name] = Ensure-Lambda -Name $def.Name -Description $def.Description
}

Write-Step "Repoint legacy action groups to new Lambdas"
$groupUpdates = @{
    "iiq-correlate" = "piter-recent-deployments"
    "iiq-context"   = "piter-service-context"
    "iiq-similar"   = "piter-similar-incidents"
}
$groups = aws bedrock-agent list-agent-action-groups --agent-id $AgentId --agent-version DRAFT | ConvertFrom-Json
foreach ($entry in $groupUpdates.GetEnumerator()) {
    $match = $groups.actionGroupSummaries | Where-Object { $_.actionGroupName -eq $entry.Key } | Select-Object -First 1
    if (-not $match) {
        Write-Host "Skipping missing action group $($entry.Key)"
        continue
    }
    $lambdaArn = $lambdaArns[$entry.Value]
    $s3Key = "agent/$($entry.Key)/openapi_schema.yaml"
    aws s3 cp "action_groups/$($entry.Value)/openapi_schema.yaml" "s3://$Bucket/$s3Key"
    if ($LASTEXITCODE -ne 0) { throw "s3 cp openapi schema failed for $($entry.Key)" }
    aws bedrock-agent update-agent-action-group `
        --agent-id $AgentId `
        --agent-version DRAFT `
        --action-group-id $match.actionGroupId `
        --action-group-name $match.actionGroupName `
        --action-group-executor "lambda=$lambdaArn" `
        --api-schema "s3=s3BucketName=$Bucket,s3ObjectKey=$s3Key" `
        --action-group-state ENABLED | Out-Null
    Write-Host "Updated $($entry.Key) -> $($entry.Value)"
}

Write-Step "Update agent instructions (keep existing agent name)"
$agent = aws bedrock-agent get-agent --agent-id $AgentId | ConvertFrom-Json
aws bedrock-agent update-agent `
    --agent-id $AgentId `
    --agent-name $agent.agent.agentName `
    --agent-resource-role-arn $agent.agent.agentResourceRoleArn `
    --foundation-model $agent.agent.foundationModel `
    --instruction file://infra/bedrock_agent_instructions.txt | Out-Null

Write-Step "Prepare agent draft"
aws bedrock-agent prepare-agent --agent-id $AgentId | Out-Null
do {
    Start-Sleep -Seconds 3
    $agentStatus = aws bedrock-agent get-agent --agent-id $AgentId --query agent.agentStatus --output text
    Write-Host "Agent status: $agentStatus"
} while ($agentStatus -eq "PREPARING")

if (-not $SkipAgentAlias) {
    Write-Step "Publish live alias (omit routingConfiguration to create new version)"
    aws bedrock-agent update-agent-alias `
        --agent-id $AgentId `
        --agent-alias-id $AgentAliasId `
        --agent-alias-name "live" | Out-Null

    $alias = aws bedrock-agent get-agent-alias --agent-id $AgentId --agent-alias-id $AgentAliasId | ConvertFrom-Json
    $newVersion = $alias.agentAlias.routingConfiguration[0].agentVersion
    Write-Host "Live alias now routes to agent version $newVersion"
}

Write-Step "KB retrieval smoke test"
aws bedrock-agent-runtime retrieve `
    --knowledge-base-id $KbId `
    --retrieval-query text="What should I check when users cannot log in after the latest deployment?" `
    --retrieval-configuration vectorSearchConfiguration="{numberOfResults=3}"

Write-Host ""
Write-Host "Done. Invoke the agent with Python (AWS CLI has no invoke-agent):" -ForegroundColor Green
Write-Host "  .\.venv\Scripts\python.exe scripts\agent_smoke_test.py"
