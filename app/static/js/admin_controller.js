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
    this.mdToast.showSimple('Updated');
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
};
