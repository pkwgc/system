<?php
use think\migration\Migrator;
use think\migration\db\Column;

class CreateOrdersTable extends Migrator
{
    public function change()
    {
        $this->table('orders')
            ->addColumn('order_id', 'string', ['limit' => 32, 'null' => false, 'comment' => '订单唯一标识'])
            ->addColumn('user_id', 'string', ['limit' => 32, 'null' => false, 'comment' => '用户ID'])
            ->addColumn('amount', 'decimal', ['precision' => 10, 'scale' => 2, 'null' => false, 'comment' => '订单金额'])
            ->addColumn('status', 'string', ['limit' => 20, 'default' => '初始化', 'comment' => '订单状态'])
            ->addColumn('create_time', 'datetime', ['null' => true])
            ->addColumn('update_time', 'datetime', ['null' => true])
            ->addIndex(['order_id'], ['unique' => true])
            ->addIndex(['user_id'])
            ->create();
    }
}
