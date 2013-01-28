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

class Topic extends CPHPDatabaseRecordClass
{
	public $table_name = "topics";
	public $fill_query = "SELECT * FROM topics WHERE `Id` = :Id";
	public $verify_query = "SELECT * FROM topics WHERE `Id` = :Id";
	
	public $prototype = array(
		'string' => array(
			'Title'			=> "Title",
			'ProviderId'		=> "ProviderId",
			'Description'		=> "Description"
		),
		'numeric' => array(
			'ParentId'		=> "ParentId",
			'Provider'		=> "Provider"
		),
		'boolean' => array(
			'NeedsEnrollment'	=> "NeedsEnrollment"
		),
		'timestamp' => array(
			'CreationDate'		=> "Created",
			'StartDate'		=> "StartDate",
			'EndDate'		=> "EndDate"
		),
		'topic' => array(
			'Parent'		=> "ParentId"
		)
	);
	
	public function __get($name)
	{
		switch($name)
		{
			case "sProviderName":
				return $this->GetProviderName();
				break;
			default:
				return parent::__get($name);
				break;
		}
	}
	
	public function GetProviderName()
	{
		switch($this->sProvider)
		{
			case 1:
				return "Khan University";
			case 2:
				return "Coursera";
			case 3:
				return "University of Reddit";
			default:
				return "Unknown";
		}
	}
	
	public function AsDataset($fetch_children = true, $fetch_items = true)
	{
		$child_data = array();
		
		if($fetch_children == true)
		{
			foreach($this->GetChildren() as $child)
			{
				$child_data[] = $child->AsDataset();
			}
		}
		
		$item_data = array();
		
		if($fetch_items == true)
		{
			foreach($this->GetItems() as $item)
			{
				$item_data[] = $item->AsDataset();
			}
		}
		
		return array(
			"title"			=> $this->uTitle,
			"description"		=> $this->uDescription,
			"created"		=> $this->sCreationDate,
			"start"			=> $this->sStartDate,
			"end"			=> $this->sEndDate,
			"provider"		=> $this->sProviderName,
			"needs_enrollment"	=> $this->sNeedsEnrollment,
			"children"		=> $child_data,
			"items"			=> $item_data
		);
	}
	
	public function GetItems()
	{
		try
		{
			return Item::CreateFromQuery("SELECT * FROM items WHERE `TopicId` = :TopicId", array(':TopicId' => $this->sId));
		}
		catch (NotFoundException $e)
		{
			return array();
		}
	}
	
	public function GetChildren()
	{
		try
		{
			return Topic::CreateFromQuery("SELECT * FROM topics WHERE `ParentId` = :ParentId", array(':ParentId' => $this->sId));
		}
		catch (NotFoundException $e)
		{
			return array();
		}
	}
}
