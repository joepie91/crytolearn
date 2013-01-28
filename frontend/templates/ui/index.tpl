<!doctype html>
<html>
	<head>
		<title>learn.cryto.net</title>
		<link rel="stylesheet" href="style.css">
		<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.9.0/jquery.min.js"></script>
		<script>
			var search_timeout = null;
			
			$(function(){
				/*$("input").val("data");
				runSearch();*/
			
				$("input").keypress(function(){
					if(typeof search_timeout !== "null")
					{
						clearTimeout(search_timeout);
					}
					
					search_timeout = setTimeout(runSearch, 800)
				});
			});
			
			function runSearch()
			{
				$(".search-large").removeClass("search-large").addClass("search-top");
				$(".spinner").show();
				var query = $("input#query").val();
				
				$.post("/api/search", {q: query}, function(response){
					$(".spinner").hide();
					$(".results").html("");
					
					for(i in response)
					{
						if(response[i].items.length > 0)
						{
							var result_wrapper = instantiateTemplate("result_wrapper");
							
							var result_block = instantiateTemplate("result_topic");
							result_block.children(".title").html(response[i].title);
							result_block.children(".providername").html(response[i].provider);
							result_block.appendTo(result_wrapper);
							
							for(x in response[i].items)
							{
								item = response[i].items[x];
								
								var item_block = instantiateTemplate("result_item");
								item_block.children(".title").html(item.title);
								item_block.children(".title").attr("href", item.url);
								item_block.children(".type").html(item.type);
								item_block.insertAfter(result_block);
							}
							
							result_wrapper.appendTo(".results");
						}
					}
					
					setHandlers();
				}, "json");
			}
			
			function setHandlers()
			{
				$(".toggler, .topic").each(
					function(){
						$(this).click(function(event){
							toggleItems(this, event);
						});
					}
				);
			}
			
			function instantiateTemplate(template_name)
			{
				var instance = $("#template_" + template_name).clone();
				instance.removeAttr("id");
				return instance;
			}
			
			function toggleItems(ctx, event)
			{
				var parent = $(ctx).parentsUntil(".wrapper");
				
				if(parent.length == 0)
				{
					var wrapper = $(ctx).parent();
				}
				else
				{
					var wrapper = parent.parent();
				}
				
				var toggler = wrapper.find(".toggler");
				
				if(typeof toggler.data("toggled") == "undefined" || toggler.data("toggled") == false)
				{
					toggler.data("toggled", true);
					toggler.html("-");
					wrapper.find(".item").show();
				}
				else
				{
					toggler.data("toggled", false);
					toggler.html("+");
					wrapper.find(".item").hide();
				}
				
				event.stopPropagation();
			}
		</script>
	</head>
	<body>
		<div class="header">
			<h1><strong>learn.cryto.net</strong> :: Learn something new!</h1>
		</div>
		<div class="main">
			<div class="search-large">
				I want to learn about <input type="text" id="query">. <img src="/static/spinner.gif" class="spinner" style="display: none;">
			</div>
			<div class="results">
				
			</div>
		</div>
		<div id="templates">
			<div id="template_result_wrapper" class="wrapper"></div>
			<div id="template_result_topic" class="topic">
				<span class="toggler">+</span>
				<strong>Topic: </strong>
				<span class="title"></span>
				<span class="providername"></span>
			</div>
			<div id="template_result_item" class="item">
				<span class="type"></span>
				<a href="#" class="title"></a>
			</div>
		</div>
	</body>
</html>
