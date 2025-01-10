<?php
namespace app\model;

use think\Model;

class Order extends Model
{
    protected $name = 'orders';
    
    protected $schema = [
        'id'          => 'int',
        'order_id'    => 'string',
        'user_id'     => 'string',
        'amount'      => 'decimal',
        'status'      => 'string',
        'create_time' => 'datetime',
        'update_time' => 'datetime'
    ];
    
    protected $autoWriteTimestamp = true;

    // Generate unique order ID
    public static function generateOrderId(): string
    {
        return date('YmdHis') . substr(md5(uniqid(mt_rand(), true)), 0, 8);
    }

    // Validate order amount
    public static function validateAmount(float $amount): bool
    {
        return $amount >= 1 && $amount <= 500;
    }
}
