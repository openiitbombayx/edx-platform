/*
IITBombayX : 9th Jan 2016
Field validation method being restored. Earlier it had been customized, now it is being set to approach similar to Open edX Cypress release.
*/
var edx = edx || {};

// IITBombayX :Validation code
(function( $, _, _s, gettext ) {
    'use strict';

    /* Mix non-conflicting functions from underscore.string
     * (all but include, contains, and reverse) into the
     * Underscore namespace. In practice, this mixin is done
     * by the access view, but doing it here helps keep the
     * utility self-contained.
     */
    _.mixin( _.str.exports() );

    edx.utils = edx.utils || {};

    var utils = (function(){
        var _fn = {
            validate: {

                msg: {
                    email: '<li><%- gettext("The email address you\'ve provided isn\'t formatted correctly.") %></li>',
                    city: '<li><%- gettext("City must contain only characters with no special character.") %></li>',
/* IITBombayX: Pin code validation message changed.*/
		    pincode: '<li><%- gettext("Pincode must be integer and should not start with 10, 01 or 00.") %></li>',
                    aadhar: '<li><%- gettext("Aadhar ID must be integer.") %></li>',
                    min: '<li><%- _.sprintf( gettext("%(field)s must have at least %(count)d characters."), context ) %></li>',
                    max: '<li><%- _.sprintf( gettext("%(field)s can only contain up to %(count)d characters."), context ) %></li>',
                    required: '<li><%- _.sprintf( gettext("Please enter your %(field)s."), context ) %></li>',
                    custom: '<li><%= content %></li>'
                },

                field: function( el ) {
                    var $el = $(el),
                        required = true,
                        min = true,
                        max = true,
                        email = true,
                        city= true,
                        pincode= true,
                        aadhar= true,
                        response = {},
                        isBlank = _fn.validate.isBlank( $el );

                    if ( _fn.validate.isRequired( $el ) ) {
                        if ( isBlank ) {
                            required = false;
                        } else {
                            min = _fn.validate.str.minlength( $el );
                            max = _fn.validate.str.maxlength( $el );
                            email = _fn.validate.email.valid( $el );
                            city = _fn.validate.city.valid( $el );
                            pincode = _fn.validate.pincode.valid( $el );
                            aadhar = _fn.validate.aadhar.valid( $el );
 
                        }
                    } else if ( !isBlank ) {
                        min = _fn.validate.str.minlength( $el );
                        max = _fn.validate.str.maxlength( $el );
                        email = _fn.validate.email.valid( $el );
                        city = _fn.validate.city.valid( $el );
                        pincode = _fn.validate.pincode.valid( $el );
                        aadhar = _fn.validate.aadhar.valid( $el );

                    }

                    response.isValid = required && min && max && email && city && pincode && aadhar;

                    if ( !response.isValid ) {
                        _fn.validate.removeDefault( $el );

                        response.message = _fn.validate.getMessage( $el, {
                            required: required,
                            min: min,
                            max: max,
                            email: email,
                            city:city,
                            pincode:pincode,
                            aadhar:aadhar
                        });
                    }

                    return response;
                },

                str: {
                    minlength: function( $el ) {
                        var min = $el.attr('minlength') || 0;

                        return min <= $el.val().length;
                    },

                    maxlength: function( $el ) {
                        var max = $el.attr('maxlength') || false;

                        return ( !!max ) ? max >= $el.val().length : true;
                    }
                },

                isRequired: function( $el ) {
                    return $el.attr('required');
                },

                isBlank: function( $el ) {
                    var type =  $el.attr('type'),
                        isBlank;

                    if ( type === 'checkbox' ) {
                        isBlank = !$el.prop('checked');
                    } else if ( type === 'select' ) {
                        isBlank = ( $el.data('isdefault') === true );
                    } else {
                        isBlank = !$el.val();
                    }

                    return isBlank;
                },

                email: {
                    // This is the same regex used to validate email addresses in Django 1.4
                    regex: new RegExp(
                        [
                            '(^[-!#$%&\'*+/=?^_`{}|~0-9A-Z]+(\\.[-!#$%&\'*+/=?^_`{}|~0-9A-Z]+)*',
                            '|^"([\\001-\\010\\013\\014\\016-\\037!#-\\[\\]-\\177]|\\\\[\\001-\\011\\013\\014\\016-\\177])*"',
                            ')@((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\\.)+[A-Z]{2,6}\\.?$)',
                            '|\\[(25[0-5]|2[0-4]\\d|[0-1]?\\d?\\d)(\\.(25[0-5]|2[0-4]\\d|[0-1]?\\d?\\d)){3}\\]$'
                        ].join(''), 'i'
                    ),

                    valid: function( $el ) {
                        return $el.attr('type') === 'email' ? _fn.validate.email.format( $el.val() ) : true;
                    },

                    format: function( str ) {
                        return _fn.validate.email.regex.test( str );
                    }
                },

                city: {
                    regex: new RegExp(
                        ['(^[a-zA-Z]*$)']
                    ),

                    valid: function( $el ) {
                        return $el.attr('name') === 'city' ? _fn.validate.city.format( $el.val() ) : true;
                    },

                    format: function( str ) {
                        return _fn.validate.city.regex.test( str );
                    }
                },

                pincode: {
                    regex: new RegExp(
			['^(1(?!0)[0-9]*|[2-9]+[0-9]*)$']
                    ),
                    valid: function( $el ) {
                        return $el.attr('name') === 'pincode' ? _fn.validate.pincode.format( $el.val() ) : true;
                    },

                    format: function( str ) {
                        return _fn.validate.pincode.regex.test( str );
                    }
                },
            
                aadhar: {
                    regex: new RegExp(
                        ['(^[0-9]*$)']
                    ),

                    valid: function( $el ) {
                        return $el.attr('name') === 'aadhar_id' ? _fn.validate.aadhar.format( $el.val() ) : true;
                    },

                    format: function( str ) {
                        return _fn.validate.aadhar.regex.test( str );
                    }
                },


                getLabel: function( id ) {
                    // Extract the field label, remove the asterisk (if it appears) and any extra whitespace
                    return $("label[for=" + id + "]").text().split("*")[0].trim();
                },

                getMessage: function( $el, tests ) {
                    var txt = [],
                        tpl,
                        label,
                        obj,
                        customMsg;

                    _.each( tests, function( value, key ) {
                        if ( !value ) {
                            label = _fn.validate.getLabel( $el.attr('id') );
                            customMsg = $el.data('errormsg-' + key) || false;

                            // If the field has a custom error msg attached, use it
                            if ( customMsg ) {
                                tpl = _fn.validate.msg.custom;

                                obj = {
                                    content: customMsg
                                };
                            } else {
                                tpl = _fn.validate.msg[key];

                                obj = {
                                    // We pass the context object to the template so that
                                    // we can perform variable interpolation using sprintf
                                    context: {
                                        field: label
                                    }
                                };

                                if ( key === 'min' ) {
                                    obj.context.count = parseInt( $el.attr('minlength'), 10 );
                                } else if ( key === 'max' ) {
                                    obj.context.count = parseInt( $el.attr('maxlength'), 10 );
                                }
                            }

                            txt.push( _.template( tpl, obj ) );
                        }
                    });

                    return txt.join(' ');
                },

                // Removes the default HTML5 validation pop-up
                removeDefault: function( $el ) {
                    if ( $el.setCustomValidity ) {
                        $el.setCustomValidity(' ');
                    }
                }
            }
        };

        return {
            validate: _fn.validate.field
        };

    })();

    edx.utils.validate = utils.validate;

})( jQuery, _, _.str, gettext );
