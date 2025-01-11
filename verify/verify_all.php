<?php
header('Content-Type: application/json');

function checkStatistics() {
    try {
        $db = new PDO(
            "mysql:host=rm-m5e0666vtv5234qi39o.mysql.rds.aliyuncs.com;dbname=stsmen;port=3306",
            "pkwgc",
            "Wghfd@584521@fd"
        );
        $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

        // Get time range from request parameters or use default (today)
        $startTime = isset($_GET['startTime']) ? $_GET['startTime'] : date('Y-m-d 00:00:00');
        $endTime = isset($_GET['endTime']) ? $_GET['endTime'] : date('Y-m-d 23:59:59');

        // Validate date format
        if (!strtotime($startTime) || !strtotime($endTime)) {
            return ["status" => "error", "message" => "Invalid date format"];
        }

        // Query for total unique phones in taozi_dx table (count each phone only once)
        $stmt = $db->prepare("
            SELECT COUNT(DISTINCT phone) as total
            FROM taozi_dx 
            WHERE shijian BETWEEN :start AND :end
        ");
        $stmt->execute(['start' => $startTime, 'end' => $endTime]);
        $totalStats = $stmt->fetch(PDO::FETCH_ASSOC);

        // Query for success records (stuta=2, allowing duplicates)
        $stmt = $db->prepare("
            SELECT COUNT(*) as success
            FROM taozi_dx 
            WHERE shijian BETWEEN :start AND :end 
            AND stuta = 2
        ");
        $stmt->execute(['start' => $startTime, 'end' => $endTime]);
        $successStats = $stmt->fetch(PDO::FETCH_ASSOC);

        // Query for project name
        $stmt = $db->prepare("
            SELECT name 
            FROM taozi_dx 
            WHERE shijian BETWEEN :start AND :end 
            LIMIT 1
        ");
        $stmt->execute(['start' => $startTime, 'end' => $endTime]);
        $nameRow = $stmt->fetch(PDO::FETCH_ASSOC);
        $projectName = $nameRow ? $nameRow['name'] : '';

        $total = intval($totalStats['total']);
        $success = intval($successStats['success']);

        return [
            "status" => "success",
            "data" => [
                "total" => $total,
                "success" => $success,
                "rate" => $total > 0 ? round(($success / $total) * 100, 2) : 0,
                "timeRange" => [
                    "start" => $startTime,
                    "end" => $endTime
                ],
                "projectName" => $projectName
            ]
        ];
    } catch (PDOException $e) {
        return ["status" => "error", "message" => $e->getMessage()];
    }
}

// Return statistics
$results = checkStatistics();
echo json_encode($results, JSON_PRETTY_PRINT);
