<?php
namespace app\controller;

use app\model\User;
use app\model\Order;
use think\Request;
use think\facade\Db;

class AdminController
{
    public function listUsers(Request $request)
    {
        try {
            $page = max(1, intval($request->get('page', 1)));
            $limit = min(50, max(1, intval($request->get('limit', 20))));
            $search = $request->get('search', '');
            
            $query = User::order('create_time', 'desc');
            
            if (!empty($search)) {
                $query->where('user_id', 'like', "%{$search}%");
            }
            
            $users = $query->paginate([
                'list_rows' => $limit,
                'page' => $page,
            ]);
            
            return json([
                'code' => 200,
                'message' => '获取用户列表成功',
                'data' => $users
            ]);
            
        } catch (\Exception $e) {
            return json(['code' => 500, 'message' => '获取用户列表失败：' . $e->getMessage()]);
        }
    }

    public function blockUser(Request $request)
    {
        Db::startTrans();
        try {
            $user_id = $request->post('user_id');
            if (empty($user_id)) {
                return json(['code' => 400, 'message' => '用户ID不能为空']);
            }
            
            $user = User::where('user_id', $user_id)->lock(true)->find();
            if (!$user) {
                return json(['code' => 404, 'message' => '用户不存在']);
            }
            
            if ($user->isAdmin()) {
                return json(['code' => 403, 'message' => '不能封禁管理员账户']);
            }
            
            $user->status = 'blocked';
            $user->save();
            
            Db::commit();
            return json(['code' => 200, 'message' => '用户封禁成功']);
            
        } catch (\Exception $e) {
            Db::rollback();
            return json(['code' => 500, 'message' => '用户封禁失败：' . $e->getMessage()]);
        }
    }

    public function unblockUser(Request $request)
    {
        Db::startTrans();
        try {
            $user_id = $request->post('user_id');
            if (empty($user_id)) {
                return json(['code' => 400, 'message' => '用户ID不能为空']);
            }
            
            $user = User::where('user_id', $user_id)->lock(true)->find();
            if (!$user) {
                return json(['code' => 404, 'message' => '用户不存在']);
            }
            
            $user->status = 'active';
            $user->save();
            
            Db::commit();
            return json(['code' => 200, 'message' => '用户解封成功']);
            
        } catch (\Exception $e) {
            Db::rollback();
            return json(['code' => 500, 'message' => '用户解封失败：' . $e->getMessage()]);
        }
    }

    public function adjustBalance(Request $request)
    {
        Db::startTrans();
        try {
            $user_id = $request->post('user_id');
            $amount = floatval($request->post('amount'));
            $reason = $request->post('reason', '管理员调整');
            
            if (empty($user_id)) {
                return json(['code' => 400, 'message' => '用户ID不能为空']);
            }
            
            $user = User::where('user_id', $user_id)->lock(true)->find();
            if (!$user) {
                return json(['code' => 404, 'message' => '用户不存在']);
            }
            
            // Use bcmath for precise decimal calculations
            $user->balance = bcadd($user->balance, $amount, 2);
            if (bccomp($user->balance, '0', 2) < 0) {
                return json(['code' => 400, 'message' => '调整后余额不能小于0']);
            }
            
            $user->save();
            
            Db::commit();
            return json([
                'code' => 200,
                'message' => '余额调整成功',
                'data' => [
                    'user_id' => $user->user_id,
                    'balance' => $user->balance,
                    'adjustment' => $amount,
                    'reason' => $reason
                ]
            ]);
            
        } catch (\Exception $e) {
            Db::rollback();
            return json(['code' => 500, 'message' => '余额调整失败：' . $e->getMessage()]);
        }
    }

    public function listOrders(Request $request)
    {
        try {
            $page = max(1, intval($request->get('page', 1)));
            $limit = min(50, max(1, intval($request->get('limit', 20))));
            $user_id = $request->get('user_id', '');
            $status = $request->get('status', '');
            $start_time = $request->get('start_time', '');
            $end_time = $request->get('end_time', '');
            
            $sort_field = $request->get('sort_field', 'create_time');
            $sort_order = $request->get('sort_order', 'desc');
            $min_amount = floatval($request->get('min_amount', 0));
            $max_amount = floatval($request->get('max_amount', 0));
            
            // Validate sort field
            $allowed_sort_fields = ['create_time', 'amount', 'status', 'user_id'];
            if (!in_array($sort_field, $allowed_sort_fields)) {
                $sort_field = 'create_time';
            }
            
            $query = Order::order($sort_field, $sort_order);
            
            if (!empty($user_id)) {
                $query->where('user_id', 'like', "%{$user_id}%");
            }
            
            if (!empty($status)) {
                // Map English status to Chinese
                $status_map = [
                    'success' => '成功',
                    'failed' => '失败',
                    'initial' => '初始化'
                ];
                $mapped_status = $status_map[$status] ?? $status;
                $query->where('status', $mapped_status);
            }
            
            // Amount range filter
            if ($min_amount > 0) {
                $query->where('amount', '>=', $min_amount);
            }
            if ($max_amount > 0) {
                $query->where('amount', '<=', $max_amount);
            }
            
            if (!empty($start_time)) {
                $query->whereTime('create_time', '>=', $start_time);
            }
            
            if (!empty($end_time)) {
                $query->whereTime('create_time', '<=', $end_time);
            }
            
            $orders = $query->paginate([
                'list_rows' => $limit,
                'page' => $page,
            ]);
            
            return json([
                'code' => 200,
                'message' => '获取订单列表成功',
                'data' => $orders
            ]);
            
        } catch (\Exception $e) {
            return json(['code' => 500, 'message' => '获取订单列表失败：' . $e->getMessage()]);
        }
    }

    public function updateOrderStatus(Request $request)
    {
        Db::startTrans();
        try {
            $order_id = $request->post('order_id');
            $status = $request->post('status');
            $reason = $request->post('reason', '管理员修改');
            
            if (empty($order_id) || empty($status)) {
                return json(['code' => 400, 'message' => '订单ID和状态不能为空']);
            }
            
            if (!in_array($status, ['初始化', '成功', '失败'])) {
                return json(['code' => 400, 'message' => '无效的订单状态']);
            }
            
            $order = Order::where('order_id', $order_id)->lock(true)->find();
            if (!$order) {
                return json(['code' => 404, 'message' => '订单不存在']);
            }
            
            // Handle refund if changing to failed status
            if ($status === '失败' && $order->status !== '失败') {
                $user = User::where('user_id', $order->user_id)->lock(true)->find();
                if ($user) {
                    $user->balance = bcadd($user->balance, $order->amount, 2);
                    $user->save();
                }
            }
            
            $order->status = $status;
            $order->save();
            
            Db::commit();
            return json([
                'code' => 200,
                'message' => '订单状态更新成功',
                'data' => [
                    'order_id' => $order->order_id,
                    'status' => $order->status,
                    'reason' => $reason
                ]
            ]);
            
        } catch (\Exception $e) {
            Db::rollback();
            return json(['code' => 500, 'message' => '订单状态更新失败：' . $e->getMessage()]);
        }
    }
}
