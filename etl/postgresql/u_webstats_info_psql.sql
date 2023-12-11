# update "Valid thrrough" date

update webstats_info 
	set value = (select max(date) from bioc_web_downloads)
	where key = 'ValidThru'
