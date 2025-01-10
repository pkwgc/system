<?php
use think\migration\Migrator;
use think\migration\db\Column;

class CreateUsersTable extends Migrator
{
    public function change()
    {
        $this->table('users')
            ->addColumn('user_id', 'string', ['limit' => 32, 'null' => false, 'comment' => '用户唯一标识'])
            ->addColumn('key', 'string', ['limit' => 32, 'null' => false, 'comment' => '用户密钥'])
            ->addColumn('balance', 'decimal', ['precision' => 10, 'scale' => 2, 'default' => '0.00', 'comment' => '账户余额'])
            ->addColumn('role', 'string', ['limit' => 20, 'default' => 'customer', 'comment' => '用户角色：customer/admin'])
            ->addColumn('status', 'string', ['limit' => 20, 'default' => 'active', 'comment' => '用户状态：active/blocked'])
            ->addColumn('create_time', 'datetime', ['null' => true])
            ->addColumn('update_time', 'datetime', ['null' => true])
            ->addIndex(['user_id'], ['unique' => true])
            ->create();
    }
}
