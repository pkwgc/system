<?php
use think\migration\Migrator;
use think\migration\db\Column;

class AddRoleAndStatusToUsers extends Migrator
{
    public function change()
    {
        $table = $this->table('users');
        $table->addColumn('role', 'string', ['limit' => 20, 'default' => 'customer', 'comment' => '用户角色：customer/admin'])
              ->addColumn('status', 'string', ['limit' => 20, 'default' => 'active', 'comment' => '用户状态：active/blocked'])
              ->update();
    }
}
