<?php
namespace app\command;

use think\console\Command;
use think\console\Input;
use think\console\Output;
use think\facade\Db;

class TestDb extends Command
{
    protected function configure()
    {
        $this->setName('test:db')
            ->setDescription('Test database connection and table creation');
    }

    protected function execute(Input $input, Output $output)
    {
        try {
            // Test connection
            $output->writeln("Testing database connection...");
            $output->writeln("Database config: " . json_encode(config('database'), JSON_PRETTY_PRINT));
            
            // Try to create the users table
            $output->writeln("Creating users table...");
            Db::execute("CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id VARCHAR(32) UNIQUE NOT NULL,
                key VARCHAR(32) NOT NULL,
                balance DECIMAL(10,2) DEFAULT 0.00,
                create_time DATETIME,
                update_time DATETIME
            )");
            
            // Check if table exists
            $tables = Db::query("SELECT name FROM sqlite_master WHERE type='table' AND name='users'");
            $output->writeln("Tables found: " . json_encode($tables));
            
            // Try to insert a test user
            $userId = substr(md5(uniqid()), 0, 16);
            $key = md5(uniqid(mt_rand(), true));
            
            Db::table('users')->insert([
                'user_id' => $userId,
                'key' => $key,
                'balance' => 500.00,
                'create_time' => date('Y-m-d H:i:s'),
                'update_time' => date('Y-m-d H:i:s')
            ]);
            
            $output->writeln("Test user created successfully!");
            $output->writeln("User ID: " . $userId);
            $output->writeln("Key: " . $key);
            
        } catch (\Exception $e) {
            $output->writeln("Error: " . $e->getMessage());
            $output->writeln("Trace: " . $e->getTraceAsString());
        }
    }
}
