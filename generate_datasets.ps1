$ErrorActionPreference = "Stop"
$baseDir = "c:\Users\OM\Desktop\College-PredictiveAI"
$datasetDir = Join-Path $baseDir "datasets"
if (!(Test-Path $datasetDir)) { New-Item -ItemType Directory -Force -Path $datasetDir | Out-Null }

$random = New-Object Random(42)
function Get-Rand([double]$min, [double]$max) { return $min + ($random.NextDouble() * ($max - $min)) }
function Get-RandInt([int]$min, [int]$max) { return $random.Next($min, $max + 1) }

# 1. Crop Data
$cropRanges = @{
    'rice' = @{ N=@(60,100); P=@(35,65); K=@(35,55); temp=@(20,28); humidity=@(78,90); ph=@(5,7.5); rainfall=@(180,300) };
    'maize' = @{ N=@(60,100); P=@(35,65); K=@(25,45); temp=@(18,30); humidity=@(55,75); ph=@(5.5,7); rainfall=@(60,120) };
    'chickpea' = @{ N=@(15,50); P=@(55,80); K=@(75,100); temp=@(17,22); humidity=@(14,20); ph=@(7,8); rainfall=@(65,100) };
}
$defaultRange = @{ N=@(20,120); P=@(10,90); K=@(15,85); temp=@(15,35); humidity=@(40,85); ph=@(5.5,7.5); rainfall=@(40,250) }
$allCrops = @('rice','maize','chickpea','kidneybeans','pigeonpeas','mothbeans','mungbean','blackgram','lentil','pomegranate','banana','mango','grapes','watermelon','muskmelon','apple','orange','papaya','coconut','cotton','jute','coffee')

$csvPath = Join-Path $datasetDir "crop_recommendation.csv"
$writer = New-Object System.IO.StreamWriter $csvPath
$writer.WriteLine("N,P,K,temperature,humidity,ph,rainfall,label")

foreach ($crop in $allCrops) {
    $r = $cropRanges[$crop]
    if ($null -eq $r) { $r = $defaultRange }
    for ($i = 0; $i -lt 100; $i++) {
        $n = Get-Rand $r['N'][0] $r['N'][1]
        $p = Get-Rand $r['P'][0] $r['P'][1]
        $k = Get-Rand $r['K'][0] $r['K'][1]
        $t = Get-Rand $r['temp'][0] $r['temp'][1]
        $h = Get-Rand $r['humidity'][0] $r['humidity'][1]
        $ph = Get-Rand $r['ph'][0] $r['ph'][1]
        $rain = Get-Rand $r['rainfall'][0] $r['rainfall'][1]
        $writer.WriteLine("{0},{1},{2},{3},{4},{5},{6},{7}", $n, $p, $k, $t, $h, $ph, $rain, $crop)
    }
}
$writer.Close()

# 2. Fertilizer Data
$soilTypes = @('Sandy','Loamy','Black','Red','Clayey')
$cropTypes = @('Maize','Sugarcane','Cotton','Tobacco','Paddy','Barley','Wheat','Oil seeds','Pulses','Ground Nuts')
$fertilizers = @('Urea','DAP','14-35-14','28-28','17-17-17','20-20','10-26-26')

$fertPath = Join-Path $datasetDir "fertilizer.csv"
$writer = New-Object System.IO.StreamWriter $fertPath
$writer.WriteLine("Temperature,Humidity,Moisture,Soil_Type,Crop_Type,Nitrogen,Phosphorus,Potassium,Fertilizer")

for ($i = 0; $i -lt 500; $i++) {
    $n = Get-RandInt 5 45
    $p = Get-RandInt 5 45
    $k = Get-RandInt 5 45
    $fert = ""
    if ($n -gt $p -and $n -gt $k) { $fert = 'Urea' }
    elseif ($p -gt $n -and $p -gt $k) { $fert = 'DAP' }
    else { $fert = $fertilizers[(Get-RandInt 0 ($fertilizers.Length - 1))] }
    
    $t = Get-Rand 20 35
    $h = Get-Rand 40 70
    $m = Get-Rand 25 65
    $soil = $soilTypes[(Get-RandInt 0 ($soilTypes.Length - 1))]
    $ct = $cropTypes[(Get-RandInt 0 ($cropTypes.Length - 1))]
    $writer.WriteLine("{0},{1},{2},{3},{4},{5},{6},{7},{8}", $t, $h, $m, $soil, $ct, $n, $p, $k, $fert)
}
$writer.Close()

# 3. Pesticide JSON
$pestObj = @{ mappings = @() }
$cropsList = @('Rice', 'Maize', 'Cotton', 'Tomato', 'Potato', 'Apple', 'Grape', 'Banana', 'Mango', 'Wheat')
$diseases = @('Blight', 'Rust', 'Rot', 'Wilt', 'Mildew', 'Spot', 'Canker', 'Scab')
$seasons = @('Kharif', 'Rabi', 'Zaid')
$pestTypes = @('Mancozeb 75% WP', 'Tricyclazole', 'Chlorothalonil', 'Copper Oxychloride')
$orgAlts = @('Neem Oil', 'Pseudomonas', 'Trichoderma', 'Bordeaux Mixture')
$safety = @('Wear gloves', 'Do not inhale spray mist')

for ($i = 0; $i -lt 40; $i++) {
    $c = $cropsList[(Get-RandInt 0 ($cropsList.Length - 1))]
    if ($i -lt 4) { $c = @('Rice', 'Maize', 'Cotton', 'Tomato')[$i] }
    $d = $diseases[(Get-RandInt 0 ($diseases.Length - 1))]
    $season = $seasons[(Get-RandInt 0 ($seasons.Length - 1))]
    $pest = $pestTypes[(Get-RandInt 0 ($pestTypes.Length - 1))]
    $org = $orgAlts[(Get-RandInt 0 ($orgAlts.Length - 1))]
    $dosage = "{0:N1} g/L" -f (Get-Rand 1 3)
    $interval = "{0} days" -f (Get-RandInt 7 20)
    
    $pestObj.mappings += @{
        crop = $c; disease = "$c $d"; season = $season;
        pesticide = $pest; organic_alternative = $org;
        dosage = $dosage; spray_interval = $interval;
        safety_precautions = $safety
    }
}
$pestJsonPath = Join-Path $datasetDir "pesticide_kb.json"
$pestObj | ConvertTo-Json -Depth 5 > $pestJsonPath

Write-Host "Datasets generated via PowerShell"
