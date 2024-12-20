const app = getApp()

Page({
  data: {
    gameId: '',
    playerId: '',
    players: {},
    communityCards: [],
    pot: 0,
    currentPlayer: null,
    isCurrentPlayer: false,
    betAmount: 0,
    minBet: 0,
    canCheck: false,
    wsConnection: null
  },

  onLoad() {
    this.data.gameId = app.globalData.gameId
    this.data.playerId = app.globalData.playerId
    this.setupWebSocket()
  },

  setupWebSocket() {
    const ws = wx.connectSocket({
      url: `${app.globalData.wsUrl}/ws/${this.data.gameId}/${this.data.playerId}`,
      success: () => {
        console.log('WebSocket connected')
      }
    })

    ws.onMessage((res) => {
      const data = JSON.parse(res.data)
      if (data.type === 'game_state') {
        this.updateGameState(data.data)
      }
    })

    ws.onClose(() => {
      console.log('WebSocket disconnected')
      setTimeout(() => this.setupWebSocket(), 1000)
    })

    this.setData({ wsConnection: ws })
  },

  updateGameState(gameState) {
    const isCurrentPlayer = gameState.current_player === this.data.playerId
    this.setData({
      players: gameState.players,
      communityCards: gameState.community_cards,
      pot: gameState.pot,
      currentPlayer: gameState.players[this.data.playerId],
      isCurrentPlayer,
      minBet: gameState.minimum_bet,
      canCheck: gameState.can_check,
      betAmount: gameState.minimum_bet
    })
  },

  onBetChange(e) {
    this.setData({
      betAmount: e.detail.value
    })
  },

  sendAction(action, amount = 0) {
    const message = {
      action,
      amount: parseInt(amount)
    }
    this.data.wsConnection.send({
      data: JSON.stringify(message)
    })
  },

  onFold() {
    this.sendAction('fold')
  },

  onCheck() {
    this.sendAction('check')
  },

  onCall() {
    this.sendAction('bet', this.data.minBet)
  },

  onRaise() {
    this.sendAction('bet', this.data.betAmount)
  },

  onUnload() {
    if (this.data.wsConnection) {
      this.data.wsConnection.close()
    }
  }
})
