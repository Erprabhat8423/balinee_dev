	$(document).on('click','.check_optional_field:visible',function(){
		attribute_id = $('.check_optional_field:visible').val();

		if($('.check_optional_field:visible').prop('checked')){
			disabled = [];
			$("input[name='"+attribute_id+"[]").each(function(){
				if($(this).prop('disabled')){
					if($(this).prop('checked')){
						$(this).prop('checked',true);
					}else{
						$(this).prop('checked',false);
					}
					disabled.push($(this).val());
				}else{
					$(this).prop('checked',true);
				}
			})
			$('#optional_'+attribute_id).val(disabled.join());

		}else{
			checked = [];
			$("input[name='"+attribute_id+"[]").each(function(){
				if($(this).prop('disabled')){
					if($(this).prop('checked')){
						$(this).prop('checked',true);
					}else{
						$(this).prop('checked',false);
					}
					checked.push($(this).val());
				}else{
					checked.push($(this).val());
					$(this).prop('checked',false);
				}
			})
			$('#optional_'+attribute_id).val(checked.join());
		}
		

	});



	function checkIfAllChecked(){
		total = $('table:visible').find('.optional_field').length;
		total_checked = 0;
		$('table:visible').find('.optional_field').each(function(){
			console.log($(this).prop('checked'));
			if($(this).prop('checked')){
				total_checked = total_checked + 1;
			}
		})
		
		if(total_checked == total){
			$('.check_optional_field:visible').prop('checked',true)
		}
	}

	function viewAttributes(url){
		if(url != ""){
			$('.loading-bg').show();
			$.ajax({
				method: "GET",
				url: url,
				success: function (data) {
					$('.loading-bg').hide();
					$('#entityAttributeModal').html(data);
					$('#entityAttributeModal').modal({show:true,backdrop: 'static', keyboard: false});
					updateAllFields();
					setTimeout(function() {

						var attributes = [2,3,4,5,6,7,8,9];
						for (var i = 0; i < attributes.length - 1; i++) {

							window['table_'+attributes[i]] = $('#table_'+attributes[i]).DataTable( {
								"ordering": false,
								"info":     false,
								mark: true,
								scrollY:        '50vh',
								scrollCollapse: true,
								paging:         false,
								fixedHeader: {
									header: true,
								},
							} );
						}

					}, 1000);




					$("#entity_attribute_id").select2();




				}
			});
		}
	}


	$(document).on('click','a[data-toggle="tab"]',function(){
		if($(this).parent().parent().parent().parent().attr('id') != "entity_type_attributes" ){
			$('.loading-bg').show();
			str = $(this).attr('href');
			var res = str.replace("#tab_content", "");
			if($('#table_'+res).length){
				$('#table_'+res).DataTable().destroy();

				setTimeout(function() {
					window['table_'+res] = $('#table_'+res).DataTable( {
						"ordering": false,
						"info":     false,
						mark: true,
						scrollY:        '50vh',
						scrollCollapse: true,
						paging:         false,
						fixedHeader: {
							header: true,
						},
					} );

					checkIfAllChecked();
					$('.loading-bg').hide();



					searchGlobally();


				}, 1000);
			}
		}

	})



 //2nd tab
 $(document).on('click',"input[name='2[]']",function(){
 	unchecked = [];
 	$("input[name='2[]'").each(function(){
 		if(!$(this).prop('checked')){
 			unchecked.push($(this).val());
 		}else{

 		}
 	})
 	$('#optional_2').val(unchecked.join());
 });


 $(document).on('click',"input[name='hidden_attr_2[]']",function(){
 	unchecked = [];
 	$("input[name='hidden_attr_2[]'").each(function(){
 		if(!$(this).prop('checked')){
 			unchecked.push($(this).val());
 		}
 	})
 	$('#hidden_2').val(unchecked.join());
 });

 //3rd tab

 $(document).on('click',"input[name='3[]']",function(){
 	unchecked = [];
 	$("input[name='3[]'").each(function(){
 		if(!$(this).prop('checked')){
 			unchecked.push($(this).val());
 		}
 	})
 	$('#optional_3').val(unchecked.join());
 });


 $(document).on('click',"input[name='hidden_attr_3[]']",function(){
 	unchecked = [];
 	$("input[name='hidden_attr_3[]'").each(function(){
 		if(!$(this).prop('checked')){
 			unchecked.push($(this).val());
 		}
 	})
 	$('#hidden_3').val(unchecked.join());
 });

 $(document).on('click',"input[name='4[]']",function(){
 	unchecked = [];
 	$("input[name='4[]'").each(function(){
 		if(!$(this).prop('checked')){
 			unchecked.push($(this).val());
 		}
 	})
 	$('#optional_4').val(unchecked.join());
 });


 $(document).on('click',"input[name='hidden_attr_4[]']",function(){
 	unchecked = [];
 	$("input[name='hidden_attr_4[]'").each(function(){
 		if(!$(this).prop('checked')){
 			unchecked.push($(this).val());
 		}
 	})
 	$('#hidden_4').val(unchecked.join());
 });

 $(document).on('click',"input[name='5[]']",function(){
 	unchecked = [];
 	$("input[name='5[]'").each(function(){
 		if(!$(this).prop('checked')){
 			unchecked.push($(this).val());
 		}
 	})
 	$('#optional_5').val(unchecked.join());
 });


 $(document).on('click',"input[name='hidden_attr_5[]']",function(){
 	unchecked = [];
 	$("input[name='hidden_attr_5[]'").each(function(){
 		if(!$(this).prop('checked')){
 			unchecked.push($(this).val());
 		}
 	})
 	$('#hidden_5').val(unchecked.join());
 });

 $(document).on('click',"input[name='6[]']",function(){
 	unchecked = [];
 	$("input[name='6[]'").each(function(){
 		if(!$(this).prop('checked')){
 			unchecked.push($(this).val());
 		}
 	})
 	$('#optional_6').val(unchecked.join());
 });


 $(document).on('click',"input[name='hidden_attr_6[]']",function(){
 	unchecked = [];
 	$("input[name='hidden_attr_6[]'").each(function(){
 		if(!$(this).prop('checked')){
 			unchecked.push($(this).val());
 		}
 	})
 	$('#hidden_6').val(unchecked.join());
 });

 $(document).on('click',"input[name='7[]']",function(){
 	unchecked = [];
 	$("input[name='7[]'").each(function(){
 		if(!$(this).prop('checked')){
 			unchecked.push($(this).val());
 		}
 	})
 	$('#optional_7').val(unchecked.join());
 });


 $(document).on('click',"input[name='hidden_attr_7[]']",function(){
 	unchecked = [];
 	$("input[name='hidden_attr_7[]'").each(function(){
 		if(!$(this).prop('checked')){
 			unchecked.push($(this).val());
 		}
 	})
 	$('#hidden_7').val(unchecked.join());
 });

 $(document).on('click',"input[name='8[]']",function(){
 	unchecked = [];
 	$("input[name='8[]'").each(function(){
 		if(!$(this).prop('checked')){
 			unchecked.push($(this).val());
 		}
 	})
 	$('#optional_8').val(unchecked.join());
 });


 $(document).on('click',"input[name='hidden_attr_8[]']",function(){
 	unchecked = [];
 	$("input[name='hidden_attr_8[]'").each(function(){
 		if(!$(this).prop('checked')){
 			unchecked.push($(this).val());
 		}
 	})
 	$('#hidden_8').val(unchecked.join());
 });


 function updateEntityAttributes(action){
 	$('#updateEntityAttributesForm').removeAttr('target');
 	$('#updateEntityAttributesForm').attr('action',action);
 	$('#updateEntityAttributesForm').submit();
 }


 function previewConfiguration(action){
 	$('#updateEntityAttributesForm').attr('action',action);
 	$('#updateEntityAttributesForm').attr('target','_blank');
 	$('#updateEntityAttributesForm').submit();
 }

 function searchGlobally(){
 	global_search = $("#global-search").val();
 	// console.log(window.table_3);
 	if(global_search != ""){

 		if($('#table_2').length){
 			window.table_2.search(global_search).draw(); 
 			var info_2 = window.table_2.page.info();
 			$('#badge_2').text(info_2.recordsDisplay);
 		}
 		if($('#table_3').length){
 			window.table_3.search(global_search).draw();
 			var info_3 = window.table_3.page.info();
 			$('#badge_3').text(info_3.recordsDisplay);
 		}
 		if($('#table_4').length){
 			window.table_4.search(global_search).draw();
 			var info_4 = window.table_4.page.info();
 			$('#badge_4').text(info_4.recordsDisplay);
 		}
 		if($('#table_5').length){
 			window.table_5.search(global_search).draw();
 			var info_5 = window.table_5.page.info();
 			$('#badge_5').text(info_5.recordsDisplay);
 		}
 		if($('#table_6').length){
 			window.table_6.search(global_search).draw();
 			var info_6 = window.table_6.page.info();
 			$('#badge_6').text(info_6.recordsDisplay);
 		}
 		if($('#table_7').length){
 			window.table_7.search(global_search).draw();
 			var info_7 = window.table_7.page.info();
 			$('#badge_7').text(info_7.recordsDisplay);
 		}
 		if($('#table_8').length){
 			window.table_8.search(global_search).draw();  
 			var info_8 = window.table_8.page.info();
 			$('#badge_8').text(info_8.recordsDisplay);
 		}
 	}else{
 		$('input[type="search"]').val('');

 		window.table_2.search('').draw();
 		window.table_3.search('').draw();
 		window.table_4.search('').draw();
 		window.table_5.search('').draw();
 		window.table_6.search('').draw();
 		window.table_7.search('').draw();
 		window.table_8.search('').draw();

 		$('#badge_2').text('');
 		$('#badge_3').text('');
 		$('#badge_4').text('');
 		$('#badge_5').text('');
 		$('#badge_6').text('');
 		$('#badge_7').text('');
 		$('#badge_8').text('');
 	}

 }

