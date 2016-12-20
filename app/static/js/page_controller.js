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

  this.recaptchaResponse_ = '';

  this.slides = [
    'Spring break 2012 in Ireland',
    'Strolling through Old Montreal',
    'Exploring a Japanese market',
    'Hiding their fear of heights on a ferris wheel in Andorra',
    'On the beach in Barcelona',
    'Kevin is not amused in London'
  ];

  this.activeSlide = 0;

  setInterval(function() {
    this.activeSlide = this.activeSlide == this.slides.length - 1 ? 0 : this.activeSlide + 1;
    this.rootScope_.$digest();
  }.bind(this), 12000);
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
    this.recaptchaResponse_ = gCaptchaResponse;
    this.invitation = resp.data;
    this.rsvpFormState = 'rsvp';
  }.bind(this), this.handleError_.bind(this));
};


PageController.prototype.sendRsvp = function() {
  this.errorMessage = null;
  if (!this.invitation) { return; }

  var errMessages = [];
  for (var i = 0; i < this.invitation.guests.length; i++) {
    if (this.invitation.guests[i].rsvp != 'coming' &&
        this.invitation.guests[i].rsvp != 'not_coming') {
      errMessages[0] = 'Please RSVP for all guests.'
    }
    if ((this.invitation.guests[i].rsvp == 'coming' && 
        !this.invitation.guests[i].food_choice)) {
      errMessages[1]= 'Please make a food selection.';
    }
  }

  if (errMessages.length) {
    this.errorMessage = errMessages.join(' ');
    return;
  }

  this.errorMessage = '';
  var params = {invitation: this.invitation, token: this.recaptchaResponse_};
  this.http_.post('/api/invitation', params).then(function(resp) {
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
