var PageController = function($window, $rootScope) {
  this.window_ = $window;

  this.rootScope_ = $rootScope;

  this.showUpArrow = this.window_.scrollY > 100;

  this.loadingMap = false;

  this.showingVenue = true;
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


angular.module('June3App', ['ngMaterial', 'duScroll'])
    .controller('PageController', ['$window', '$rootScope', PageController])
    .value('duScrollOffset', 54);
