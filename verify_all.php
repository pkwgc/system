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

        // Get min and max dates first
        $dateRangeStmt = $db->query("
            SELECT 
                MIN(time) as min_date,
                MAX(time) as max_date
            FROM taozi_dx
        ");
        $dateRange = $dateRangeStmt->fetch(PDO::FETCH_ASSOC);

        // Query for all records in taozi_dx table with stuta=2 success condition
        $stmt = $db->prepare("
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN stuta = 2 THEN 1 END) as success,
                MIN(time) as first_record,
                MAX(time) as last_record
            FROM taozi_dx 
            WHERE time BETWEEN :start AND :end
        ");
        $stmt->execute(['start' => $startTime, 'end' => $endTime]);
        $stats = $stmt->fetch(PDO::FETCH_ASSOC);

        // Format the response with all date information
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
                ],
                "tableRange" => [
                    "min_date" => $dateRange['min_date'],
                    "max_date" => $dateRange['max_date']
                ],
                "debug_info" => [
                    "query_time" => date('Y-m-d H:i:s'),
                    "table_name" => "taozi_dx",
                    "unique_phones" => false
                ]
            ]
        ];
    } catch (PDOException $e) {
        return ["status" => "error", "message" => $e->getMessage()];
    }
}

// Debug mode to describe table structure
if (isset($_GET['debug']) && $_GET['debug'] == 'describe_taozi') {
    try {
        $db = new PDO(
            "mysql:host=rm-m5e887h8uuaul5991wo.mysql.rds.aliyuncs.com;dbname=stsmen;port=3306",
            "pkwgc",
            "Wghfd@584521@fd"
        );
        $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

        // Get table structure
        $stmt = $db->query("DESCRIBE taozi_dx");
        $structure = $stmt->fetchAll(PDO::FETCH_ASSOC);

        // Get sample data with stuta=2 condition
        $stmt = $db->query("
            SELECT 
                COUNT(*) as total_records,
                COUNT(CASE WHEN stuta = 2 THEN 1 END) as success_records,
                MIN(time) as first_record,
                MAX(time) as last_record
            FROM taozi_dx
        ");
        $stats = $stmt->fetch(PDO::FETCH_ASSOC);

        // Get distribution of stuta values
        $stmt = $db->query("
            SELECT stuta, COUNT(*) as count
            FROM taozi_dx
            GROUP BY stuta
            ORDER BY count DESC
        ");
        $stutaDistribution = $stmt->fetchAll(PDO::FETCH_ASSOC);

        echo json_encode([
            'status' => 'success',
            'data' => [
                'table_structure' => $structure,
                'statistics' => $stats,
                'stuta_distribution' => $stutaDistribution
            ]
        ], JSON_PRETTY_PRINT);
    } catch (PDOException $e) {
        echo json_encode([
            'status' => 'error',
            'message' => $e->getMessage()
        ]);
    }
}

// Return normal statistics
$results = checkStatistics();
echo json_encode($results, JSON_PRETTY_PRINT);
}
