var PageController = function($window, $rootScope, $http) {
  this.window_ = $window;

  this.rootScope_ = $rootScope;

  this.http_ = $http;

  this.showUpArrow = this.window_.scrollY > 100;

  this.loadingMap = false;

  this.showingVenue = true;

  this.invitationCode = null;

  this.invitation = null;

  this.foodChoices = [
    {'id': 1234, 'name': 'Fish', 'description': 'A fish'},
    {'id': 2345, 'name': 'Steak', 'description': 'Steak'},
    {'id': 3456, 'name': 'Chicken', 'description': 'Chicken'},
    {'id': 4567, 'name': 'Vegetarian', 'description': 'Veggies'}
  ];

  console.log(this);
};


PageController.prototype.$onInit = function() {
  this.window_.addEventListener('scroll', this.updateShowArrow_.bind(this));
  this.setLoading_(3000);
};


PageController.prototype.updateShowArrow_ = function() {
  var showUpArrow = this.window_.scrollY > 100;
  if (showUpArrow != this.showUpArrow) {
    this.showUpArrow = showUpArrow;
    this.rootScope_.$digest();
  }
};


PageController.prototype.showVenue = function() {
  this.setLoading_();
  this.showingVenue = true;
};


PageController.prototype.showHotel = function() {
  this.setLoading_();
  this.showingVenue = false;
};


PageController.prototype.setLoading_ = function(opt_delay) {
  this.loadingMap = true;
  this.window_.setTimeout(function() {
    this.loadingMap = false;
    this.rootScope_.$digest();
  }.bind(this), opt_delay || 1000);
};


PageController.prototype.lookUpInvitation = function() {
  if (!this.invitationCode || (this.invitation && this.invitationCode == this.invitation.code)) { return; }
  var config = {params: {'code': this.invitationCode}};
  this.http_.get('/api/invitation', config).then(function(resp) {
    this.invitation = resp.data;
  }.bind(this));
};


PageController.prototype.sendRsvp = function() {
  if (!this.invitation) { return; }
  this.http_.post('/api/invitation', this.invitation).then(function(resp) {
    console.log(resp.data);
  });
};


angular.module('June3App', ['ngMaterial', 'duScroll'])
    .controller('PageController', ['$window', '$rootScope', '$http', PageController])
    .value('duScrollOffset', 54);
