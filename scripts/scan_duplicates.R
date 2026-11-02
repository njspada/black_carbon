# Run from the repository: Rscript scripts/scan_duplicates.R
# Exact equality across original fields; no rounding, filling, or deletion.
library(data.table)
setNumericRounding(0)

scan_duplicates <- function(x) {
  x <- copy(as.data.table(x))
  fields <- copy(names(x))
  stopifnot(all(c("SensorID", "date") %in% fields), !"source_record_number" %in% fields)
  x[, source_record_number := .I]
  extra <- duplicated(x, by=fields)
  exact_member <- extra | duplicated(x, by=fields, fromLast=TRUE)
  keys <- c("SensorID", "date")
  valid_key <- !is.na(x$SensorID) & nzchar(x$SensorID) & !is.na(x$date)
  repeated <- valid_key & (duplicated(x, by=keys) | duplicated(x, by=keys, fromLast=TRUE))
  details <- copy(x[repeated])
  groups <- details[, .(rows=.N, distinct_rows=uniqueN(.SD),
                       first_source_record=if (.N) min(source_record_number) else NA_integer_),
                    by=keys, .SDcols=fields]
  groups[, classification := fifelse(distinct_rows == 1L, "identical_only", "conflicting")]
  groups[, extra_exact_rows := rows - distinct_rows]
  setorder(groups, SensorID, date)
  groups[, group_id := .I]
  details <- merge(details, groups[, c(keys, "group_id", "classification"), with=FALSE],
                   by=keys, all.x=TRUE, sort=FALSE)
  setorder(details, group_id, source_record_number)
  measurements <- setdiff(fields, keys)
  changes <- details[classification == "conflicting", .(
    differing_columns=paste(measurements[vapply(.SD, uniqueN, integer(1)) > 1L], collapse=", ")),
    by=group_id, .SDcols=measurements]
  groups <- merge(groups, changes, by="group_id", all.x=TRUE, sort=FALSE)
  groups[is.na(differing_columns), differing_columns := ""]
  per_sensor <- x[, .(total_rows=.N), by=SensorID]
  repeats <- groups[, .(repeated_key_groups=.N, rows_in_repeated_keys=sum(rows),
    identical_only_groups=sum(classification == "identical_only"),
    conflicting_groups=sum(classification == "conflicting"),
    extra_exact_rows_in_valid_keys=sum(extra_exact_rows)), by=SensorID]
  per_sensor <- merge(per_sensor,repeats,by="SensorID",all.x=TRUE)
  for (field in setdiff(names(per_sensor), "SensorID")) set(per_sensor,which(is.na(per_sensor[[field]])),field,0)
  exact_counts <- x[, .(exact_duplicate_member_rows=sum(exact_member[.I]),
                        extra_exact_rows=sum(extra[.I])), by=SensorID]
  per_sensor <- merge(per_sensor,exact_counts,by="SensorID",all.x=TRUE)
  summary <- data.table(metric=c("total_rows", "exact_duplicate_groups", "exact_duplicate_member_rows",
    "extra_exact_rows", "rows_with_missing_key", "repeated_sensor_timestamp_groups",
    "rows_in_repeated_sensor_timestamps", "identical_only_key_groups", "conflicting_key_groups",
    "rows_in_conflicting_keys", "extra_exact_rows_within_conflicting_keys"),
    value=c(nrow(x), sum(exact_member)-sum(extra), sum(exact_member), sum(extra), sum(!valid_key),
      nrow(groups), sum(groups$rows), sum(groups$classification == "identical_only"),
      sum(groups$classification == "conflicting"), groups[classification == "conflicting",sum(rows)],
      groups[classification == "conflicting",sum(extra_exact_rows)]))
  stopifnot(sum(per_sensor$total_rows) == nrow(x), sum(per_sensor$extra_exact_rows) == sum(extra),
            sum(groups$rows) == nrow(details), all(groups$distinct_rows <= groups$rows))
  list(summary=summary, per_sensor=per_sensor, groups=groups, details=details,
       exact_rows=x[exact_member], missing_keys=x[!valid_key])
}

main <- function() {
  script <- sub("^--file=", "", commandArgs()[grepl("^--file=",commandArgs())][1])
  root <- dirname(dirname(normalizePath(script)))
  source <- file.path(root,"data/Black Carbon Concentrations.RDS")
  out <- file.path(root,"duplicate_review")
  local <- file.path(root,"data/duplicate_review")
  dir.create(out,showWarnings=FALSE)
  dir.create(local,showWarnings=FALSE,recursive=TRUE)
  writeLines("running; prior reports have not yet been refreshed",file.path(out,"status.txt"))
  cat("Reading full RDS...\n")
  x <- readRDS(source)
  stopifnot(inherits(x$date,"POSIXct"), identical(attr(x$date,"tzone"),"UTC"))
  cat("Scanning",nrow(x),"rows across",ncol(x),"original columns...\n")
  result <- scan_duplicates(x)
  fwrite(result$summary,file.path(out,"summary.csv"))
  fwrite(result$per_sensor,file.path(out,"by_sensor.csv"))
  coordinate_patterns <- result$details[classification == "conflicting", .(
    rows=.N,
    latitude_nonmissing_values=uniqueN(Latitude[!is.na(Latitude)]),
    longitude_nonmissing_values=uniqueN(Longitude[!is.na(Longitude)]),
    any_missing_latitude=anyNA(Latitude), any_missing_longitude=anyNA(Longitude)), by=group_id][,
      .(groups=.N,rows=sum(rows)), by=.(latitude_nonmissing_values,longitude_nonmissing_values,
                                     any_missing_latitude,any_missing_longitude)]
  fwrite(coordinate_patterns,file.path(out,"coordinate_conflict_patterns.csv"))
  writeLines(paste(unname(tools::md5sum(source)),basename(source)),file.path(out,"source_md5.txt"))
  # Full row extracts stay in ignored data/. Small examples can be versioned.
  fwrite(result$groups,file.path(local,"all_repeated_key_groups.csv"))
  fwrite(result$details,file.path(local,"all_repeated_key_rows.csv"))
  fwrite(result$exact_rows,file.path(local,"all_exact_duplicate_rows.csv"))
  fwrite(result$missing_keys,file.path(local,"missing_key_rows.csv"))
  examples <- result$groups[, head(.SD,10), by=classification]
  fwrite(examples,file.path(out,"example_groups.csv"))
  fwrite(result$details[group_id %in% examples$group_id][,head(.SD,5),by=group_id],
         file.path(out,"example_rows.csv"))
  print(result$summary)
  print(result$per_sensor)
  writeLines(c("complete", paste("Source:",basename(source)),
    paste("Completed UTC:",format(Sys.time(),tz="UTC",usetz=TRUE)),
    "No source records changed or removed.",
    "Exact numeric equality; matching missing values count as equal; no timestamp rounding.",
    "Repeated-key checks exclude missing sensor IDs or timestamps; those rows are exported separately."),
    file.path(out,"status.txt"))
}

if (sys.nframe() == 0L) main()
