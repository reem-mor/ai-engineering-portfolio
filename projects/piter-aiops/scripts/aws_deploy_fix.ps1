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

# Canonical KB prefix — must match PITER_S3_PREFIX / app.config.S3_PREFIX and KB data source inclusion.
$KbPrefix = "projects/piter-aiops/knowledge_base/"
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
    if (-not (Test-Path $zip)) { throw "Failed to build Lambda zip for $Name" }
    return (Resolve-Path -LiteralPath $zip).Path
}

function Invoke-Aws([string[]]$AwsArgs) {
    $prevEap = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    & aws @AwsArgs
    $exit = $LASTEXITCODE
    $ErrorActionPreference = $prevEap
    return $exit
}

function Get-ZipFileUri([string]$ZipPath) {
    # AWS CLI on Windows requires forward slashes in fileb:// URIs.
    $resolved = (Resolve-Path -LiteralPath $ZipPath).Path.Replace("\", "/")
    return "fileb://$resolved"
}

function Test-LambdaExists([string]$Name) {
    $output = & aws lambda get-function --function-name $Name 2>$null
    return $LASTEXITCODE -eq 0
}

function Wait-LambdaReady([string]$Name) {
    do {
        $state = aws lambda get-function-configuration --function-name $Name `
            --query "{Status:LastUpdateStatus,Reason:LastUpdateStatusReason}" `
            --output json 2>$null | ConvertFrom-Json
        if ($state.Status -eq "Successful") { return }
        if ($state.Status -eq "Failed") {
            throw "Lambda $Name update failed: $($state.Reason)"
        }
        Start-Sleep -Seconds 2
    } while ($true)
}

function Update-LambdaCode([string]$Name, [string]$ZipPath) {
    $zipUri = Get-ZipFileUri $ZipPath
    & aws lambda update-function-code --function-name $Name --zip-file $zipUri | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "update-function-code failed for $Name (exit $LASTEXITCODE, zip $zipUri)"
    }
    Wait-LambdaReady $Name
}

function Ensure-Lambda([string]$Name, [string]$Description) {
    $zip = New-ActionGroupZip $Name
    $exists = Test-LambdaExists $Name

    if ($exists) {
        Update-LambdaCode -Name $Name -ZipPath $zip
        Write-Host "Updated Lambda $Name"
    } else {
        $zipUri = Get-ZipFileUri $zip
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
            "--zip-file", $zipUri
        )
        if ($createExit -ne 0) {
            if (Test-LambdaExists $Name) {
                Update-LambdaCode -Name $Name -ZipPath $zip
                Write-Host "Updated Lambda $Name (create reported conflict)"
            } else {
                throw "create-function failed for $Name"
            }
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

function Remove-OldIamPolicyVersions([string]$PolicyArn) {
    $versions = aws iam list-policy-versions --policy-arn $PolicyArn --output json | ConvertFrom-Json
    foreach ($entry in $versions.Versions) {
        if ($entry.IsDefaultVersion) { continue }
        if ((Invoke-Aws @("iam", "delete-policy-version", "--policy-arn", $PolicyArn, "--version-id", $entry.VersionId)) -eq 0) {
            Write-Host "Deleted IAM policy version $($entry.VersionId)"
        }
    }
}

Write-Step "Ensure Bedrock KB role can read knowledge_base S3 prefix"
$kbS3PolicyArn = "arn:aws:iam::${AccountId}:policy/service-role/AmazonBedrockS3PolicyForKnowledgeBase_2q8xn"
$kbS3PolicyPath = Join-Path $RepoRoot "infra/kb_s3_policy_patch.json"
$policyDocUri = (Resolve-Path -LiteralPath $kbS3PolicyPath).Path.Replace("\", "/")
$policyExit = Invoke-Aws @(
    "iam", "create-policy-version",
    "--policy-arn", $kbS3PolicyArn,
    "--policy-document", "file://$policyDocUri",
    "--set-as-default"
)
if ($policyExit -ne 0) {
    Write-Host "KB S3 policy update failed; pruning non-default versions and retrying"
    Remove-OldIamPolicyVersions $kbS3PolicyArn
    $policyExit = Invoke-Aws @(
        "iam", "create-policy-version",
        "--policy-arn", $kbS3PolicyArn,
        "--policy-document", "file://$policyDocUri",
        "--set-as-default"
    )
}
if ($policyExit -ne 0) {
    Write-Host "KB S3 policy update skipped (verify default version includes $KbPrefix)"
}

Write-Step "Sync knowledge_base markdown to S3 (canonical prefix)"
aws s3 sync (Join-Path $RepoRoot "knowledge_base") "s3://$Bucket/$KbPrefix" --exclude "*" --include "*.md" --delete

Write-Step "Point KB data source at knowledge_base S3 prefix"
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

$ingestion = aws bedrock-agent get-ingestion-job `
    --knowledge-base-id $KbId `
    --data-source-id $DataSourceId `
    --ingestion-job-id $IngestionJobId `
    --output json | ConvertFrom-Json
$stats = $ingestion.ingestionJob.statistics
Write-Host ($stats | ConvertTo-Json -Compress)
$failed = [int]($stats.numberOfDocumentsFailed)
if ($failed -gt 0) {
    Write-Host "Ingestion failures:" -ForegroundColor Yellow
    foreach ($reason in $ingestion.ingestionJob.failureReasons) {
        Write-Host $reason
    }
    throw "KB ingestion failed for $failed document(s). Check Bedrock KB IAM s3 GetObject on $KbPrefix"
}

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
$groupUpdates = @(
    @{ ActionGroup = "iiq-correlate"; Lambda = "piter-recent-deployments"; S3Key = "agent/iiq-correlate/openapi_schema.yaml" },
    @{ ActionGroup = "iiq-context"; Lambda = "piter-service-context"; S3Key = "agent/iiq-context/openapi_schema.yaml" },
    @{ ActionGroup = "iiq-similar"; Lambda = "piter-similar-incidents"; S3Key = "agent/iiq-similar/openapi_schema.yaml" },
    @{ ActionGroup = "piter-escalation"; Lambda = "piter-escalation"; S3Key = "agent/piter-escalation/openapi_schema.yaml" }
)
$agJsonDir = Join-Path $RepoRoot "dist/action-groups"
New-Item -ItemType Directory -Force -Path $agJsonDir | Out-Null
$groups = aws bedrock-agent list-agent-action-groups --agent-id $AgentId --agent-version DRAFT | ConvertFrom-Json
foreach ($entry in $groupUpdates) {
    $match = $groups.actionGroupSummaries | Where-Object { $_.actionGroupName -eq $entry.ActionGroup } | Select-Object -First 1
    if (-not $match) {
        Write-Host "Skipping missing action group $($entry.ActionGroup)"
        continue
    }
    $lambdaArn = $lambdaArns[$entry.Lambda]
    aws s3 cp "action_groups/$($entry.Lambda)/openapi_schema.yaml" "s3://$Bucket/$($entry.S3Key)"
    if ($LASTEXITCODE -ne 0) { throw "s3 cp openapi schema failed for $($entry.ActionGroup)" }
    $agPayload = @{
        agentId = $AgentId
        agentVersion = "DRAFT"
        actionGroupId = $match.actionGroupId
        actionGroupName = $match.actionGroupName
        actionGroupExecutor = @{ lambda = $lambdaArn }
        apiSchema = @{
            s3 = @{
                s3BucketName = $Bucket
                s3ObjectKey = $entry.S3Key
            }
        }
        actionGroupState = "ENABLED"
    } | ConvertTo-Json -Depth 6 -Compress
    $agPath = Join-Path $agJsonDir "$($entry.ActionGroup).json"
    [System.IO.File]::WriteAllText($agPath, $agPayload)
    $agUri = (Resolve-Path -LiteralPath $agPath).Path.Replace("\", "/")
    & aws bedrock-agent update-agent-action-group --cli-input-json "file://$agUri" | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "update-agent-action-group failed for $($entry.ActionGroup)" }
    Write-Host "Updated $($entry.ActionGroup) -> $($entry.Lambda)"
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
