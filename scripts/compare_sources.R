library(data.table)
args <- commandArgs(trailingOnly = TRUE)
stopifnot(length(args) == 3)
rds_path <- normalizePath(args[1])
csv_path <- normalizePath(args[2])
out <- args[3]
dir.create(out, showWarnings = FALSE)
sink(file.path(out, "inspection_log.txt"), split = TRUE)
cat("RDS and CSV fidelity inspection\n")
r <- readRDS(rds_path)
c <- fread(csv_path, colClasses = list(character = c("SensorID", "date")), na.strings = "NA")
cat("RDS dimensions:", dim(r), "\nCSV dimensions:", dim(c), "\n")
stopifnot(identical(names(r), names(c)), nrow(r) == nrow(c))
cat("RDS timestamp class:", class(r$date), "\nRDS timezone:", attr(r$date, "tzone"), "\n")
stopifnot(inherits(r$date, "POSIXct"), identical(attr(r$date, "tzone"), "UTC"))
same <- function(a, b) (is.na(a) & is.na(b)) | (!is.na(a) & !is.na(b) & a == b)
comparisons <- lapply(setdiff(names(r), "date"), function(n) {
  a <- r[[n]]; b <- c[[n]]
  numeric <- is.numeric(a) && is.numeric(b)
  delta <- if (numeric) abs(a - b) else NULL
  data.frame(column=n, rds_class=paste(class(a), collapse="/"),
    csv_class=paste(class(b), collapse="/"), rds_missing=sum(is.na(a)),
    csv_missing=sum(is.na(b)), missing_mask_differences=sum(xor(is.na(a),is.na(b))),
    exact_value_differences=sum(!same(a,b)),
    differences_above_1e_9=if(numeric) sum(delta > 1e-9, na.rm=TRUE) else NA,
    maximum_absolute_difference=if(numeric && any(!is.na(delta))) max(delta, na.rm=TRUE) else NA)
})
comparison <- do.call(rbind, comparisons)
print(comparison, row.names=FALSE)
write.csv(comparison, file.path(out, "column_comparison.csv"), row.names=FALSE)
date_only <- grepl("^\\d{4}-\\d{2}-\\d{2}$", c$date)
idx <- which(date_only)
expected <- format(r$date, "%Y-%m-%d %H:%M:%S", tz="UTC")
normalized <- c$date
normalized[idx] <- paste0(normalized[idx], " 00:00:00")
timestamp_mismatches <- which(!same(expected, normalized) |
  (!is.na(r$date) & as.numeric(r$date) %% 1 != 0))
fractional <- sum(as.numeric(r$date) %% 1 != 0, na.rm=TRUE)
cat("Date-only CSV records:", length(idx), "\n")
cat("Missing timestamps in RDS:", sum(is.na(r$date)), "\n")
cat("Missing timestamps in CSV:", sum(is.na(c$date) | c$date == ""), "\n")
cat("RDS fractional-second timestamps:", fractional, "\n")
cat("Timestamp mismatches after explicitly expanding date-only CSV values for comparison:", length(timestamp_mismatches), "\n")
cat("RDS midnight records:", sum(as.numeric(r$date) %% 86400 == 0, na.rm=TRUE), "\n")
review <- data.frame(source_record_number=idx, SensorID=c$SensorID[idx],
 csv_date=c$date[idx], rds_timestamp_utc=expected[idx],
 rds_epoch_seconds=as.numeric(r$date[idx]),
 rds_is_exact_midnight=as.numeric(r$date[idx]) %% 86400 == 0)
review$all_other_fields_exact_match <- Reduce(`&`, lapply(setdiff(names(r), "date"), function(n) same(r[[n]][idx],c[[n]][idx])))
write.csv(review, file.path(out,"date_only_comparison.csv"),row.names=FALSE)
cat("All affected records match other fields exactly:", all(review$all_other_fields_exact_match), "\n")
print(head(review, 5), row.names=FALSE)
neighbors <- sort(unique(c(idx-1L,idx,idx+1L)))
neighbors <- neighbors[neighbors >= 1 & neighbors <= nrow(r)]
write.csv(data.frame(source_record_number=neighbors, SensorID=r$SensorID[neighbors],
 csv_date=c$date[neighbors], rds_timestamp_utc=expected[neighbors],
 affected=neighbors %in% idx), file.path(out,"neighboring_timestamps.csv"),row.names=FALSE)
write.csv(data.frame(source_record_number=timestamp_mismatches,
 csv_date=c$date[timestamp_mismatches], rds_date=expected[timestamp_mismatches],
 rds_epoch_seconds=as.numeric(r$date[timestamp_mismatches])),
 file.path(out,"other_timestamp_differences.csv"),row.names=FALSE)
cat("\nR formatting demonstration (not evidence of the actual export process):\n")
if (length(idx)) print(as.character(r$date[idx[1]]))
cat("\nSession details:\n")
print(sessionInfo())
sink()
different <- any(comparison$exact_value_differences > 0) || length(timestamp_mismatches) > 0
if (different) {
  cat("Differences found. Row-wise differences can also reflect reordered records. No source was modified.\n")
  quit(status=2)
}
