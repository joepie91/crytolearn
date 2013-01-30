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

class Item extends CPHPDatabaseRecordClass
{
	public $table_name = "items";
	public $fill_query = "SELECT * FROM items WHERE `Id` = :Id";
	public $verify_query = "SELECT * FROM items WHERE `Id` = :Id";
	
	public $prototype = array(
		'string' => array(
			'Title'			=> "Title",
			'Description'		=> "Description",
			'SourceUrl'		=> "SourceUrl",
			'ItemUrl'		=> "ItemUrl"
		),
		'numeric' => array(
			'Type'			=> "Type",
			'Provider'		=> "Provider",
			'Views'			=> "Views",
			'TopicId'		=> "TopicId",
			'ParentId'		=> "ParentId"
		),
		'boolean' => array(
			'HasTopic'		=> "HasTopic"
		),
		'timestamp' => array(
			'CreationDate'		=> "Date",
			'StartDate'		=> "StartDate",
			'EndDate'		=> "EndDate"
		),
		'topic' => array(
			'Topic'			=> "TopicId"
		),
		'item' => array(
			'Parent'		=> "ParentId"
		)
	);
	
	public function __get($name)
	{
		switch($name)
		{
			case "sTypeName":
				return $this->GetTypeName();
				break;
			case "sProviderName":
				return $this->GetProviderName();
				break;
			default:
				return parent::__get($name);
				break;
		}
	}
	
	public function GetTypeName()
	{
		switch($this->sType)
		{
			case 1:
				return "topic";
			case 2:
				return "course";
			case 3:
				return "video";
			case 4:
				return "article";
			case 5:
				return "exercise";
			case 6:
				return "quiz";
			case 7:
				return "test";
			case 8:
				return "book";
			case 9:
				return "audiobook";
			default:
				return "unknown";
		}
	}
	
	public function GetProviderName()
	{
		switch($this->sProvider)
		{
			case 1:
				return "Khan Academy";
			case 2:
				return "Coursera";
			case 3:
				return "University of Reddit";
			default:
				return "Unknown";
		}
	}
	
	public function GetChildren()
	{
		try
		{
			return Item::CreateFromQuery("SELECT * FROM items WHERE `ParentId` = :ParentId", array(':ParentId' => $this->sId));
		}
		catch (NotFoundException $e)
		{
			return array();
		}
	}
	
	public function AsDataset($fetch_children = true)
	{
		$child_data = array();
		
		if($fetch_children == true)
		{
			foreach($this->GetChildren() as $child)
			{
				$child_data[] = $child->AsDataset();
			}
		}
		
		return array(
			"title"		=> $this->uTitle,
			"description"	=> $this->uDescription,
			"url"		=> $this->uItemUrl,
			"source"	=> $this->uSourceUrl,
			"created"	=> $this->sCreationDate,
			"start"		=> $this->sStartDate,
			"end"		=> $this->sEndDate,
			"type"		=> $this->sTypeName,
			"provider"	=> $this->sProviderName,
			"views"		=> $this->sViews,
			"children"	=> $child_data
		);
	}
}
