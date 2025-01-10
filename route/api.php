<?php
use think\facade\Route;

// API routes group
Route::group('api', function () {
    // User authentication routes
    Route::post('auth/login', 'Auth/login');
    
    // Customer routes - protected by auth middleware
    Route::group('customer', function () {
        Route::get('profile', 'CustomerController/profile');
        Route::get('transactions', 'CustomerController/transactions');
        Route::post('settings', 'CustomerController/updateSettings');
    })->middleware([\app\middleware\Auth::class]);
    
    // Admin routes - protected by auth and admin middleware
    Route::group('admin', function () {
        Route::get('users', 'AdminController/listUsers');
        Route::post('users/block', 'AdminController/blockUser');
        Route::post('users/unblock', 'AdminController/unblockUser');
        Route::post('users/adjust_balance', 'AdminController/adjustBalance');
        Route::get('orders', 'AdminController/listOrders');
        Route::post('orders/update_status', 'AdminController/updateOrderStatus');
    })->middleware([\app\middleware\Auth::class, \app\middleware\AdminAuth::class]);
    
    // Order management routes - protected by auth middleware
    Route::group(function () {
        Route::post('orders/submit', 'OrderController/submit');
        Route::get('orders/status/:id', 'OrderController/status');
        Route::get('orders/batch', 'OrderController/batchGet');
        Route::post('orders/callback', 'OrderController/callback');
    })->middleware([\app\middleware\Auth::class]);
})->allowCrossDomain();
