var PageController = function($window, $rootScope, $http) {
  this.window_ = $window;

  this.rootScope_ = $rootScope;

  this.http_ = $http;

  this.showUpArrow = this.window_.scrollY > 100;

  this.loadingMap = false;

  this.showingVenue = true;

  this.invitationCode = null;

  this.invitation = null;

  this.foodChoices = [];

  this.rsvpFormState = 'initial';

  this.recaptchaId = 'recaptcha-container';

  this.recaptchaKey = '6Lc1Rw0UAAAAAE0Ny9GzKrFE6bukJoAbO-a82CGf';
};


PageController.prototype.$onInit = function() {
  this.window_.addEventListener('scroll', this.updateShowArrow_.bind(this));
  
  this.setLoading_(3000);
  
  this.http_.get('/api/food_choice').then(function(resp) {
    this.foodChoices = resp.data;
  }.bind(this));

  //this.renderCaptcha();
};


// PageController.prototype.renderCaptcha = function() {
//   if (!this.window_.grecaptcha) {
//     setTimeout(this.renderCaptcha.bind(this), 10);
//     return;
//   }
//   this.window_.grecaptcha.render(document.getElementById(this.recaptchaId), {
//     callback: this.recaptchaSuccess_.bind(this),
//     sitekey: this.recaptchaKey
//   });
// }


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
  this.errorMessage = null;
  if (!this.invitationCode) { return; }
  this.window_.grecaptcha.render(document.getElementById(this.recaptchaId), {
    callback: this.recaptchaSuccess_.bind(this),
    sitekey: this.recaptchaKey
  });
  this.rsvpFormState = 'recaptcha';
};


PageController.prototype.recaptchaSuccess_ = function(gCaptchaResponse) {
  console.log(arguments);
  var config = {
    params: {
      'code': this.invitationCode,
      'g-recaptcha-response': gCaptchaResponse
    }
  };
  this.http_.get('/api/invitation', config).then(function(resp) {
    this.invitation = resp.data;
  }.bind(this), this.handleError_.bind(this));
};


PageController.prototype.sendRsvp = function() {
  this.errorMessage = null;
  if (!this.invitation) { return; }
  this.http_.post('/api/invitation', this.invitation).then(function(resp) {
    console.log(resp.data);
  }.bind(this), this.handleError_.bind(this));
};


PageController.prototype.handleError_ = function(resp) {
  this.errorMessage = resp.data.error;
  this.window_.grecaptcha.reset();
  this.rsvpFormState = 'initial';
};

angular.module('June3App', ['ngMaterial', 'duScroll'])
    .controller('PageController', ['$window', '$rootScope', '$http', PageController])
    .value('duScrollOffset', 54);
