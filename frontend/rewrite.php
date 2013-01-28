<?php
$_APP = true;
require("includes/base.php");

$sPageContents = "";

$router = new CPHPRouter();

$router->allow_slash = true;
$router->ignore_query = true;

$router->routes = array(
	0 => array(
		"^/$"							=> "modules/ui/index.php",
		"^/api/search$"						=> "modules/api/search.php",
		"^/api/dump$"						=> "modules/api/dump.php"
	)
);

try
{
	$router->RouteRequest();
}
catch (RouterException $e)
{
	http_status_code(404);
	$sPageContents = "404 not found";
}

echo($sPageContents);

/*
$data = array();

foreach(Topic::CreateFromQuery("SELECT * FROM topics WHERE `ParentId` = 0") as $topic)
{
	$data[] = $topic->AsDataset();
}

echo(json_encode($data));
* */
