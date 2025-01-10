<?php
namespace app\middleware;

use app\model\User;
use think\Request;
use think\facade\Log;

class Auth
{
    public function handle(Request $request, \Closure $next)
    {
        // Log API request
        Log::info('API Request', [
            'path' => $request->pathinfo(),
            'method' => $request->method(),
            'ip' => $request->ip(),
            'params' => $request->param(),
            'headers' => array_filter($request->header(), function($key) {
                return !in_array(strtolower($key), ['authorization', 'cookie']);
            }, ARRAY_FILTER_USE_KEY)
        ]);

        $token = $request->header('Authorization');
        if (empty($token)) {
            return json(['code' => 401, 'message' => '未授权访问', 'data' => null]);
        }

        $user = User::getUserFromToken($token);
        if (!$user) {
            return json(['code' => 401, 'message' => 'Token无效或已过期', 'data' => null]);
        }

        if ($user->status !== 'active') {
            return json(['code' => 403, 'message' => '账户已被封禁', 'data' => null]);
        }
        
        // Add user to request for controllers
        $request->user = $user;
        return $next($request);
    }
}
