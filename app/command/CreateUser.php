<?php
namespace app\command;

use app\model\User;
use think\console\Command;
use think\console\Input;
use think\console\input\Argument;
use think\console\Output;

class CreateUser extends Command
{
    protected function configure()
    {
        $this->setName('user:create')
            ->addArgument('balance', Argument::OPTIONAL, '初始余额', 0.00)
            ->setDescription('创建新用户并生成凭证');
    }

    protected function execute(Input $input, Output $output)
    {
        try {
            $balance = floatval($input->getArgument('balance'));
            
            $user = new User;
            $user->user_id = substr(md5(uniqid()), 0, 16);
            $user->key = User::generateKey();
            $user->balance = $balance;
            $user->role = 'customer';
            $user->status = 'active';
            $user->save();

            $output->writeln("用户创建成功！");
            $output->writeln("User ID: " . $user->user_id);
            $output->writeln("Key: " . $user->key);
            $output->writeln("Balance: " . $user->balance);
            $output->writeln("Role: " . $user->role);
            $output->writeln("Status: " . $user->status);
        } catch (\Exception $e) {
            $output->writeln("<error>创建用户失败: " . $e->getMessage() . "</error>");
            return 1;
        }
    }
}
