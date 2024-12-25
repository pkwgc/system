<?php
header('Content-Type: application/json');

function checkStatistics() {
    try {
        $db = new PDO(
            "mysql:host=rm-m5e887h8uuaul5991wo.mysql.rds.aliyuncs.com;dbname=stsmen;port=3306",
            "pkwgc",
            "Wghfd@584521@fd"
        );
        $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

        // Get time range from request parameters or use default (today)
        $startTime = isset($_GET['startTime']) ? $_GET['startTime'] : date('Y-m-d 00:00:00');
        // End time is not used in the query as per example format
        $endTime = isset($_GET['endTime']) ? $_GET['endTime'] : date('Y-m-d 23:59:59');

        // Validate and format dates
        $startDateTime = DateTime::createFromFormat('Y-m-d H:i:s', $startTime);
        $endDateTime = DateTime::createFromFormat('Y-m-d H:i:s', $endTime);
        
        if (!$startDateTime || !$endDateTime) {
            return ["status" => "error", "message" => "Invalid date format"];
        }
        
        if ($startDateTime > $endDateTime) {
            return ["status" => "error", "message" => "开始时间不能晚于结束时间"];
        }
        
        // Format dates for SQL query
        $startTime = $startDateTime->format('Y-m-d H:i:s');
        $endTime = $endDateTime->format('Y-m-d H:i:s');

        // Get unique phone count
        $stmt1 = $db->prepare("
            SELECT COUNT(DISTINCT phone) as total
            FROM taozi_dx 
            WHERE shijian > :start
        ");
        $stmt1->execute(['start' => $startTime]);
        $uniquePhones = $stmt1->fetch(PDO::FETCH_ASSOC);

        // Get success count (stuta=2)
        $stmt2 = $db->prepare("
            SELECT COUNT(*) as success,
                MIN(shijian) as first_record,
                MAX(shijian) as last_record
            FROM taozi_dx 
            WHERE shijian > :start AND stuta = 2
        ");
        $stmt2->execute(['start' => $startTime]);
        $successStats = $stmt2->fetch(PDO::FETCH_ASSOC);

        // Combine results
        $stats = [
            'total' => $uniquePhones['total'],
            'success' => $successStats['success'],
            'first_record' => $successStats['first_record'],
            'last_record' => $successStats['last_record']
        ];
        
        // Stats are already fetched and combined above

        // Format the response
        return [
            "status" => "success",
            "data" => [
                "total" => intval($stats['total']),
                "success" => intval($stats['success']),
                "rate" => $stats['total'] > 0 ? round(($stats['success'] / $stats['total']) * 100, 2) : 0,
                "timeRange" => [
                    "start" => $startTime,
                    "end" => $endTime,
                    "first_record" => $stats['first_record'],
                    "last_record" => $stats['last_record']
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
