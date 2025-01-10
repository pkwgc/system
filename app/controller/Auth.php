<?php
namespace app\controller;

use app\model\User;
use think\Request;

class Auth
{
    public function login(Request $request)
    {
        try {
            $user_id = $request->post('user_id');
            $key = $request->post('key');

            if (empty($user_id) || empty($key)) {
                return json(['code' => 400, 'message' => '用户ID和密钥不能为空']);
            }

            $user = User::where('user_id', $user_id)
                       ->where('key', $key)
                       ->where('status', 'active')
                       ->find();
                       
            if (!$user) {
                return json(['code' => 401, 'message' => '用户ID或密钥错误']);
            }

            $token = $user->generateToken();
            
            return json([
                'code' => 200,
                'message' => '登录成功',
                'data' => [
                    'token' => $token,
                    'expire' => env('TOKEN.TOKEN_EXPIRE', 7200)
                ]
            ]);
        } catch (\Exception $e) {
            return json(['code' => 500, 'message' => '登录失败：' . $e->getMessage()]);
        }
    }
}
