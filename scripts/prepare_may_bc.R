# Run from any directory. Keeps every source reading selected by California date.
library(data.table)
script <- sub("^--file=", "", grep("^--file=", commandArgs(), value=TRUE)[1])
root <- dirname(dirname(normalizePath(script)))
out <- file.path(root, "may26")
dir.create(out, showWarnings=FALSE)
source <- readRDS(file.path(root,"data","Black Carbon Concentrations.RDS"))
start <- as.numeric(as.POSIXct("2026-05-01 00:00:00",tz="America/Los_Angeles"))
end <- as.numeric(as.POSIXct("2026-06-01 00:00:00",tz="America/Los_Angeles"))
indices <- which(!is.na(source$date) & as.numeric(source$date)>=start & as.numeric(source$date)<end)
x <- as.data.table(source[indices,,drop=FALSE])
original_fields <- copy(names(x))
x[, date_california := format(date,tz="America/Los_Angeles",format="%Y-%m-%dT%H:%M:%S%z")]
stopifnot(all(substr(x$date_california,1,7)=="2026-05"), !anyNA(x$BC))
fwrite(x,file.path(out,"bc_may2026_california.csv"),dateTimeAs="ISO",na="NA")
x[, hour_california := paste0(substr(date_california,1,13),":00:00",substr(date_california,20,24))]
x[, c("mean_bc","p95_bc","reading_count") := list(mean(BC),as.numeric(quantile(BC,0.95,type=7)),.N), by=.(SensorID,hour_california)]
path <- file.path(out,"bc_may2026_hourly.csv")
fwrite(x,path,dateTimeAs="ISO",na="NA")
saved <- fread(path,colClasses=c(date_california="character",hour_california="character"),na.strings="NA")
stopifnot(nrow(saved)==length(indices),identical(names(saved),names(x)),identical(as.numeric(saved$date),as.numeric(source$date[indices])),identical(saved$SensorID,source$SensorID[indices]))
for (field in setdiff(original_fields,c("SensorID","date"))) {
  expected <- source[[field]][indices]
  stopifnot(identical(is.na(saved[[field]]),is.na(expected)),isTRUE(all.equal(as.numeric(saved[[field]]),as.numeric(expected),tolerance=1e-14)))
}
# Verify the monthly CSV and enriched CSV have identical original fields in order.
a <- fread(file.path(out,"bc_may2026_california.csv"),colClasses="character",na.strings="NA")
b <- fread(path,colClasses="character",na.strings="NA")
for (field in names(a)) stopifnot(identical(a[[field]],b[[field]]))
hours <- x[,.(rows=.N,reading_count=unique(reading_count),mean_bc=unique(mean_bc),p95_bc=unique(p95_bc)),by=.(SensorID,hour_california)]
stopifnot(all(hours$rows==hours$reading_count),sum(hours$rows)==nrow(x),isTRUE(all.equal(sum(hours$mean_bc*hours$rows),sum(x$BC),tolerance=1e-12)))
for (i in c(1L,as.integer(nrow(hours)/2),nrow(hours))) {
  readings <- x[SensorID==hours$SensorID[i] & hour_california==hours$hour_california[i],BC]
  stopifnot(isTRUE(all.equal(hours$p95_bc[i],as.numeric(quantile(readings,0.95,type=7)))))
}
cat(sprintf("Verified %s original readings, %s sensors, %s sensor-hours; %s negative readings retained; %s records with coordinates.\n",nrow(x),uniqueN(x$SensorID),nrow(hours),sum(x$BC<0),sum(is.finite(x$Latitude)&is.finite(x$Longitude))))
