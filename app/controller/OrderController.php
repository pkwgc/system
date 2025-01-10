<?php
namespace app\controller;

use app\model\Order;
use app\model\User;
use think\Request;
use think\facade\Db;

class OrderController
{
    public function submit(Request $request)
    {
        try {
            // Get amount from request
            $amount = floatval($request->post('amount'));
            
            // Validate amount
            if (!Order::validateAmount($amount)) {
                return json(['code' => 400, 'message' => '订单金额必须在1-500元之间', 'data' => null]);
            }
            
            // Get user from middleware
            $user = $request->user;
            
            Db::startTrans();
            try {
                // Lock user record for update
                $user = User::where('user_id', $user->user_id)->lock(true)->find();
                if (!$user) {
                    Db::rollback();
                    return json(['code' => 404, 'message' => '用户不存在', 'data' => null]);
                }
                
                // Check balance
                if (bccomp($user->balance, $amount, 2) < 0) {
                    Db::rollback();
                    return json(['code' => 400, 'message' => '账户余额不足', 'data' => null]);
                }
                
                // Create order
                $order = new Order;
                $order->order_id = Order::generateOrderId();
                $order->user_id = $user->user_id;
                $order->amount = $amount;
                $order->status = '初始化';
                $order->save();
                
                // Deduct balance using bcmath
                $user->balance = bcsub($user->balance, $amount, 2);
                $user->save();
                
                Db::commit();
                
                return json([
                    'code' => 200,
                    'message' => '订单创建成功',
                    'data' => [
                        'order_id' => $order->order_id,
                        'amount' => $order->amount,
                        'status' => $order->status,
                        'balance' => $user->balance
                    ]
                ]);
            } catch (\Exception $e) {
                Db::rollback();
                throw $e;
            }
        } catch (\Exception $e) {
            return json(['code' => 500, 'message' => '订单创建失败：' . $e->getMessage(), 'data' => null]);
        }
    }

    public function status(Request $request, string $id)
    {
        try {
            $order = Order::where('order_id', $id)->find();
            if (!$order) {
                return json(['code' => 404, 'message' => '订单不存在', 'data' => null]);
            }
            
            // Verify user owns this order
            if ($order->user_id !== $request->user->user_id) {
                return json(['code' => 403, 'message' => '无权访问此订单', 'data' => null]);
            }
            
            return json([
                'code' => 200,
                'message' => '查询成功',
                'data' => [
                    'order_id' => $order->order_id,
                    'amount' => $order->amount,
                    'status' => $order->status,
                    'create_time' => $order->create_time
                ]
            ]);
        } catch (\Exception $e) {
            return json(['code' => 500, 'message' => '查询失败：' . $e->getMessage(), 'data' => null]);
        }
    }

    public function batchGet(Request $request)
    {
        try {
            // Get limit parameter, default to 10 if not provided
            $limit = min(intval($request->get('limit', 10)), 10);
            
            // Get unprocessed orders for this user
            $orders = Order::where('user_id', $request->user->user_id)
                         ->where('status', '初始化')
                         ->limit($limit)
                         ->select();
            
            if ($orders->isEmpty()) {
                return json(['code' => 404, 'message' => '没有可获取的订单', 'data' => null]);
            }
            
            $results = [];
            Db::startTrans();
            try {
                foreach ($orders as $order) {
                    // Process order here (alternate success/failure for testing)
                    static $counter = 0;
                    $success = ($counter++ % 2) == 0; // Alternate between success and failure
                    
                    if ($success) {
                        $order->status = '成功';
                    } else {
                        $order->status = '失败';
                        // Refund logic
                        $user = User::where('user_id', $order->user_id)->lock(true)->find();
                        if ($user) {
                            $user->balance = bcadd($user->balance, $order->amount, 2);
                            $user->save();
                        }
                    }
                    $order->save();
                    
                    $results[] = [
                        'order_id' => $order->order_id,
                        'amount' => $order->amount,
                        'status' => $order->status,
                        'create_time' => $order->create_time
                    ];
                }
                
                Db::commit();
                return json([
                    'code' => 200,
                    'message' => '订单处理完成',
                    'data' => $results
                ]);
            } catch (\Exception $e) {
                Db::rollback();
                throw $e;
            }
        } catch (\Exception $e) {
            return json(['code' => 500, 'message' => '订单处理失败：' . $e->getMessage(), 'data' => null]);
        }
    }

    public function callback(Request $request)
    {
        try {
            $order_id = $request->post('order_id');
            $success = $request->post('success', false);
            
            if (empty($order_id)) {
                return json(['code' => 400, 'message' => '订单ID不能为空', 'data' => null]);
            }
            
            Db::startTrans();
            try {
                $order = Order::where('order_id', $order_id)->lock(true)->find();
                if (!$order) {
                    Db::rollback();
                    return json(['code' => 404, 'message' => '订单不存在', 'data' => null]);
                }
                
                // Only process orders in initial state
                if ($order->status !== '初始化') {
                    Db::rollback();
                    return json(['code' => 400, 'message' => '订单状态不允许更新', 'data' => null]);
                }
                
                if ($success) {
                    $order->status = '成功';
                } else {
                    $order->status = '失败';
                    // Refund logic
                    $user = User::where('user_id', $order->user_id)->lock(true)->find();
                    if ($user) {
                        $user->balance = bcadd($user->balance, $order->amount, 2);
                        $user->save();
                    }
                }
                $order->save();
                
                Db::commit();
                return json([
                    'code' => 200,
                    'message' => '订单状态更新成功',
                    'data' => [
                        'order_id' => $order->order_id,
                        'status' => $order->status,
                        'refunded' => !$success
                    ]
                ]);
            } catch (\Exception $e) {
                Db::rollback();
                throw $e;
            }
        } catch (\Exception $e) {
            return json(['code' => 500, 'message' => '订单状态更新失败：' . $e->getMessage()]);
        }
    }
}
