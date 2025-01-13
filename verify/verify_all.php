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

        // Query for statistics grouped by project name
        $stmt = $db->prepare("
            SELECT 
                COALESCE(name, '') as projectName,
                COUNT(DISTINCT phone) as total,
                SUM(CASE WHEN stuta = 2 THEN 1 ELSE 0 END) as success
            FROM taozi_dx 
            WHERE shijian BETWEEN :start AND :end
            GROUP BY name
        ");
        $stmt->execute(['start' => $startTime, 'end' => $endTime]);
        $projectStats = $stmt->fetchAll(PDO::FETCH_ASSOC);

        // Process statistics for each project
        $projects = [];
        foreach ($projectStats as $stat) {
            $total = intval($stat['total']);
            $success = intval($stat['success']);
            // Ensure projectName is never null
            $projectName = empty($stat['projectName']) ? '' : $stat['projectName'];
            $projects[] = [
                "projectName" => $projectName,
                "total" => $total,
                "success" => $success,
                "rate" => $total > 0 ? round(($success / $total) * 100, 2) : 0
            ];
        }

        return [
            "status" => "success",
            "data" => [
                "projects" => $projects,
                "timeRange" => [
                    "start" => $startTime,
                    "end" => $endTime
                ]
            ]
        ];
    } catch (PDOException $e) {
        return ["status" => "error", "message" => $e->getMessage()];
    }
}

// Return statistics
$results = checkStatistics();
echo json_encode($results, JSON_PRETTY_PRINT);
