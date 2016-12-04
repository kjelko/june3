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
  this.errorMessage = null;
  if (!this.invitationCode) { return; }
  var el = document.getElementById(this.recaptchaId)
  el.innerHTML = '';  
  this.window_.grecaptcha.render(el.appendChild(document.createElement('div')), {
    callback: this.recaptchaSuccess_.bind(this),
    sitekey: this.recaptchaKey
  });
  this.rsvpFormState = 'recaptcha';
};


PageController.prototype.recaptchaSuccess_ = function(gCaptchaResponse) {
  var config = {
    params: {
      'code': this.invitationCode,
      'g-recaptcha-response': gCaptchaResponse
    }
  };
  this.http_.get('/api/invitation', config).then(function(resp) {
    this.invitation = resp.data;
    this.rsvpFormState = 'rsvp';
  }.bind(this), this.handleError_.bind(this));
};


PageController.prototype.sendRsvp = function() {
  this.errorMessage = null;
  if (!this.invitation) { return; }
  this.http_.post('/api/invitation', this.invitation).then(function(resp) {
    this.invitation = null;
    this.invitationCode = null;
    this.rsvpFormState = 'final';
  }.bind(this), this.handleError_.bind(this));
};


PageController.prototype.handleError_ = function(resp) {
  this.errorMessage = resp.data.error;
  this.rsvpFormState = 'initial';
  this.window_.grecaptcha.reset();
};


AdminController = function ($rootScope, $http, $mdToast) {
  this.rootScope_ = $rootScope;
  
  this.http_ = $http;

  this.invitations = [];

  this.guests = [];

  this.isLoading = true;

  this.foodChoices = [];

  this.mdToast = $mdToast;

  this.stats = {
    numGuests: 0,
    numResponded: 0,
    numAttending: 0,
    foodChoices: {}
  };
};


AdminController.prototype.$onInit = function() {
  this.http_.get('/admin/api/invitation').then(this.parseInivitations_.bind(this));

  this.http_.get('/api/food_choice').then(function(resp) {
    this.foodChoices = resp.data || [];
  }.bind(this));
};


AdminController.prototype.parseInivitations_ = function(resp) {
  this.invitations = resp.data;
  for (var i = 0; i < this.invitations.length; i++) {
    for (var j = 0; j < this.invitations[i].guests.length; j++) {
      var guest = this.invitations[i].guests[j];
      this.guests.push(guest);
      if (guest.rsvp == 'coming') {
        this.stats.numAttending++;
        this.stats.numResponded++;
        if (guest.food_choice) {
          this.foodChoices[guest.food_choice.name] = 
              this.foodChoices[guest.food_choice.name] || 0;
          this.foodChoices[guest.food_choice.name]++;
        } 
      } else if (guest.rsvp == 'not_coming') {
        this.stats.numResponded++;
      }
    }
  }
  this.stats.numGuests = this.guests.length;
  this.isLoading = false;
}


AdminController.prototype.updateFoodChoice = function(foodChoice) {
  this.http_.post('/admin/api/food_choice', foodChoice).then(function() {
    this.mdToast.shoSimple('Updated');
  }.bind(this));
};


AdminController.prototype.createFoodChoice = function(event) {
  var foodChoice = event.target.elements;
  this.http_.post('/admin/api/food_choice', {
    'name': foodChoice.name.value,
    'description': foodChoice.description.value,
  }).then(function(resp) {
    foodChoice.name.value = '';
    foodChoice.description.value = '';
    this.foodChoices.push(resp.data);
    this.mdToast.showSimple('Created');
  }.bind(this));
};


AdminController.prototype.deleteFoodChoice = function(foodChoice) {
  this.http_.delete('/admin/api/food_choice', {params: foodChoice}).then(function(resp) {
    for (var i = 0; i < this.foodChoices.length; i++) {
      if (this.foodChoices[i].id == foodChoice.id) {
        this.foodChoices.splice(i, 1);
      }
    }
    this.mdToast.showSimple('Deleted');
  }.bind(this));
}


var config = function($mdThemingProvider) {
  $mdThemingProvider.definePalette('june3Primary', 
    $mdThemingProvider.extendPalette('green', {
      '600': '#adc67b'
    }));
  $mdThemingProvider.definePalette('june3Accent', 
    $mdThemingProvider.extendPalette('orange', {
      '600': '#df862d',
      'A700': '#fecb9c',
      'contrastLightColors': ['600']
    }));
  $mdThemingProvider.theme('default')
    .primaryPalette('june3Primary', {'default': '600'})
    .accentPalette('june3Accent', {'default': '600'})
    .warnPalette('red', {'default': '600'});
};

angular.module('June3App', ['ngMaterial', 'duScroll'])
    .controller('PageController', ['$window', '$rootScope', '$http', PageController])
    .controller('AdminController', ['$rootScope', '$http', '$mdToast', AdminController])
    .config(['$mdThemingProvider', config])
    .value('duScrollOffset', 54);
