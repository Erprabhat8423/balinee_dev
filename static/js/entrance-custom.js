$(document).ready(function(){
	$('#otpbox').hide();
	$('.btnshow').click(function(){
		$('#otpbox').toggle();
	})
});

// function accept_terms(candidate_id) {
// 	if ($('#agree_terms').is(':checked')) {
// 		// console.log("Agreed")
// 		// window.location.href = '/quiz-start'
// 		url = '/quiz-start'
// 		var candidate_id = 3 // {{candidate_id}}
// 		console.log("Candidate ID: ", candidate_id)
// 		$.ajax({
// 			url: url,
// 			method: "POST",
// 			data: {
// 				candidate_id : candidate_id
// 			},
// 			success: function(data) {
// 				console.log("Data: ", data)
// 			},
// 			error: function(error) {
// 				console.log("Error: ", error)
// 			}

// 		});
// 	}
// 	else {
// 		console.log("Not Agreed")
// 	}
// }



// window.onbeforeunload = function (e) {
// 	var message = "Are you sure ?"
// 	var firefox = /Firefox[\/\s](\d+)/.test(navigator.userAgent);
// 	if (firefox) {
// 	    //Add custom dialog
// 	    //Firefox does not accept window.showModalDialog(), window.alert(), window.confirm(), and window.prompt() furthermore
// 	    var dialog = document.createElement("div");
// 	    document.body.appendChild(dialog);
// 	    dialog.id = "dialog";
// 	    dialog.style.visibility = "hidden";
// 	    dialog.innerHTML = message;
// 	    var left = document.body.clientWidth / 2 - dialog.clientWidth / 2;
// 	    dialog.style.left = left + "px";
// 	    dialog.style.visibility = "visible";
// 	    var shadow = document.createElement("div");
// 	    document.body.appendChild(shadow);
// 	    shadow.id = "shadow";
// 	    //tip with setTimeout
// 	    setTimeout(function () {
// 	        document.body.removeChild(document.getElementById("dialog"));
// 	        document.body.removeChild(document.getElementById("shadow"));
// 	    }, 0);
// 	}
// 	return message;
// };

// function showLoader() {
// 	console.log("Show Loader")
// 	$("#loader").show();
// 	$("#bodyContainer").addClass('isBlurred');
// }

// function hideLoader() {
// 	console.log("Hide Loader")
// 	$("#loader").hide();
// 	$("#bodyContainer").removeClass('isBlurred');
// }


function generateOTP() {
                contact = $('#contact').val()
                url = "/registration"
                $.ajax({
                    url: url,
                    method: 'POST',
                    data: {
                        contact:contact
                    },
                    success: function (data) {
                        // hideLoader();
                        $('#otpbox').show();
                    },
                    error: function (err) {
                        document.getElementById('contact_error').innerHTML = 'Please enter registered mobile number';
                    }
                });
            }

            function submitOTP() {
                otp = $('#otp').val()
                contact = $('#contact').val()
                url = "/checking-OTP"
                $.ajax({
                    url: url,
                    method: 'GET',
                    data: {
                        contact:contact,
                        otp:otp
                    },
                    success: function (data) {
                        // hideLoader();
						// document.cookie = "id=" + candidate_id + ";" + (60*60) + ";path=/"
                        $('body').html('')
                        $('body').html(data)
                    },
                    error: function (err) {
                        console.log(err)
                        document.getElementById('otp_error').innerHTML = 'Invalid OTP';
                    }
                });
            }

            function declineTerms(candidate_id) {
                $.ajax({
                    url: '/quiz-terms-decline',
                    method: "GET",
                    data: {
                        candidate_id: candidate_id
                    },
                    success: function(data){
                        window.location.href = '/registration'
                    }
                });
            }

            function accept_terms(candidate_id) {
                if ($('#agree_terms').is(':checked')) {
                    url = '/quiz-start'
                    $.ajax({
                        url: url,
                        method: "POST",
                        data: {
                            candidate_id : candidate_id
                        },
                        success: function(data) {
                            // $('html').html("")
							document.cookie = "id=" + candidate_id + ";" + (60*60) + ";path=/"
                            $('body').html(data)
                        },
                        error: function(error) {
                            console.log("Error: ", error)
                        }
                    });
                }
                else {
                    $('.check-group label:before').css("border", "2px solid #f30000 !important")
                }
            }

            function startQuiz(candidate_id) {
				url = '/quiz-questions'
				$.ajax({
					url: url,
					method: "GET",
					data: {
						candidate_id: candidate_id
					},
					success: function(data) {
						debugger
                        document.cookie = "id=" + candidate_id + ";" + (60*60) + ";path=/"
                        $('body').html("")
                        $('body').html(data)
					},
					error: function(err) {
						console.log("Error")
					}
				})
			}

            $(window).bind( 'beforeunload' , function(event) {
				return 'Are you sure?';
			} ).bind( 'unload', function(event) {
				document.cookie = 'id=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
			} );


            // window.onbeforeunload = function (e) {
            //     debugger;
				// document.cookie = 'id=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
                // var message = "Are you sure ?";
                // var firefox = /Firefox[\/\s](\d+)/.test(navigator.userAgent);
                // var mozilla = /Mozilla[\/\s](\d+)/.test(navigator.userAgent);
                // if (mozilla) {
                //     //Add custom dialog
                //     //Firefox does not accept window.showModalDialog(), window.alert(), window.confirm(), and window.prompt() furthermore
                //     var dialog = document.createElement("div");
                //     document.body.appendChild(dialog);
                //     dialog.id = "dialog";
                //     dialog.style.visibility = "hidden";
                //     dialog.innerHTML = message;
                //     var left = document.body.clientWidth / 2 - dialog.clientWidth / 2;
                //     dialog.style.left = left + "px";
                //     dialog.style.visibility = "visible";
                //     var shadow = document.createElement("div");
                //     document.body.appendChild(shadow);
                //     shadow.id = "shadow";
                //     //tip with setTimeout
                //     setTimeout(function () {
                //         document.body.removeChild(document.getElementById("dialog"));
                //         document.body.removeChild(document.getElementById("shadow"));
                //     }, 0);
                // }
                // return message;
                // return 'I want My text here';
            // }





$(document).ready(function(){
	$(document).on("keydown", disableF5);
});

function disableF5(e) { if ((e.which || e.keyCode) == 116 || (e.which || e.keyCode) == 82) e.preventDefault(); };