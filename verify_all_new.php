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

        // Get unique phone count and success count
        $stmt = $db->prepare("
            WITH unique_phones AS (
                SELECT COUNT(DISTINCT phone) as total
                FROM taozi_dx 
                WHERE shijian BETWEEN :start AND :end
            ),
            success_records AS (
                SELECT COUNT(*) as success_count
                FROM taozi_dx 
                WHERE shijian BETWEEN :start AND :end
                AND stuta = 2
            ),
            date_range AS (
                SELECT 
                    MIN(shijian) as first_record,
                    MAX(shijian) as last_record
                FROM taozi_dx
                WHERE shijian BETWEEN :start AND :end
            )
            SELECT 
                p.total,
                s.success_count as success,
                d.first_record,
                d.last_record
            FROM unique_phones p
            CROSS JOIN success_records s
            CROSS JOIN date_range d
        ");
        
        $stmt->execute(['start' => $startTime, 'end' => $endTime]);
        $stats = $stmt->fetch(PDO::FETCH_ASSOC);

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
