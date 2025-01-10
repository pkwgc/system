<?php
namespace app\controller;

use app\model\User;
use app\model\Order;
use think\Request;
use think\facade\Db;

class CustomerController
{
    public function profile(Request $request)
    {
        try {
            $user = $request->user;
            
            return json([
                'code' => 200,
                'message' => '获取个人信息成功',
                'data' => [
                    'user_id' => $user->user_id,
                    'balance' => $user->balance,
                    'status' => $user->status,
                    'create_time' => $user->create_time
                ]
            ]);
        } catch (\Exception $e) {
            return json(['code' => 500, 'message' => '获取个人信息失败：' . $e->getMessage()]);
        }
    }

    public function transactions(Request $request)
    {
        try {
            $page = max(1, intval($request->get('page', 1)));
            $limit = min(50, max(1, intval($request->get('limit', 20))));
            $start_time = $request->get('start_time', '');
            $end_time = $request->get('end_time', '');
            
            $query = Order::where('user_id', $request->user->user_id)
                         ->order('create_time', 'desc');
            
            if (!empty($start_time)) {
                $query->whereTime('create_time', '>=', $start_time);
            }
            
            if (!empty($end_time)) {
                $query->whereTime('create_time', '<=', $end_time);
            }
            
            $transactions = $query->paginate([
                'list_rows' => $limit,
                'page' => $page,
            ]);
            
            return json([
                'code' => 200,
                'message' => '获取交易记录成功',
                'data' => $transactions
            ]);
        } catch (\Exception $e) {
            return json(['code' => 500, 'message' => '获取交易记录失败：' . $e->getMessage()]);
        }
    }

    public function updateSettings(Request $request)
    {
        try {
            $user = $request->user;
            // Add any user-configurable settings here
            // For now, just return success
            return json([
                'code' => 200,
                'message' => '设置更新成功',
                'data' => [
                    'user_id' => $user->user_id,
                    'settings_updated' => true
                ]
            ]);
        } catch (\Exception $e) {
            return json(['code' => 500, 'message' => '设置更新失败：' . $e->getMessage()]);
        }
    }
}
