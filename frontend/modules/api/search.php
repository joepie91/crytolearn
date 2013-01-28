<?php
/*
 * Cryto Learn is more free software. It is licensed under the WTFPL, which
 * allows you to do pretty much anything with it, without having to
 * ask permission. Commercial use is allowed, and no attribution is
 * required. We do politely request that you share your modifications
 * to benefit other developers, but you are under no enforced
 * obligation to do so :)
 * 
 * Please read the accompanying LICENSE document for the full WTFPL
 * licensing text.
 */

if(!isset($_APP)) { die("Unauthorized."); }

if(empty($_POST['q']))
{
	die(json_encode(array(
		"error" => "No search query specified."
	)));
}
else
{
	$query = $_POST['q'];
	$terms = explode(" ", $query);
	
	$db_query_terms = array();
	$valid_term = false;
	
	foreach($terms as $term)
	{
		$db_query_terms[] = "`Title` LIKE ?";
		$term = str_replace("%", "\%", $term);
		$term = str_replace("_", "\_", $term);
		$valid_term = $valid_term || (strlen($term) >= 2);
		$db_query_arguments[] = "%{$term}%";
	}
	
	if($valid_term)
	{
		$db_query = implode(" AND ", $db_query_terms);
		array_unshift($db_query_arguments, '');
		unset($db_query_arguments[0]);
		
		try
		{
			$results_topics = Topic::CreateFromQuery("SELECT * FROM topics WHERE {$db_query}", $db_query_arguments);
			
			$return_objects = array();
		
			foreach($results_topics as $topic)
			{
				$return_objects[] =  $topic->AsDataset();
			}
			
			$sPageContents = json_encode($return_objects);
		}
		catch (NotFoundException $e)
		{
			$sPageContents = json_encode(array("error" => "No results found for the specified query.", "query" => $query));
		}
	}
	else
	{
		die(json_encode(array(
			"error" => "No valid search query specified."
		)));
	}
}
