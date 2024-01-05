# global_package_history.R
library(tidyverse)
library(glue)
library(rvest)
library(xml2)
library(curl)
# TODO CLeanup and operationalize

# create a data frame consisting of release, biocViews category, package for all history
# the package version are from the admin/manifest Bioc project:
# git clone git@git.bioconductor.org:admin/manifest
# The description of the packages will be in 
# Get the releases from https://bioconductor.org/about/release-announcements/ by web scraping

outfile_location <- "~/Downloads/manifest_to_packages_table.csv"
table_data_location <- "~/Downloads/packages_table-data.csv"

manifest_template <- "https://www.bioconductor.org/packages/{version}/{category}/src/contrib/PACKAGES"

# get all packages for each release 
manifest <- \( major, minor) {
  categories = c("bioc", "data/annotation", "data/experiment")
  # the workflows category first appeared in 2.13
  if (major > 2 || (major == 2 && minor > 12))
  {
    categories <- append(categories, "workflows")
  }
  list_rbind(mapply(\(category, version) {
  
    print(glue("{category} / {version}"))

      con <- curl(glue(manifest_template))
    result <- read.dcf(con)
    close(con)
    tibble(category, package = result[,1])
    },
         categories, glue("{major}.{minor}"), SIMPLIFY = FALSE))
}

file_path <- "conversion/bioc_versions.html"
html_data <- read_html(file_path)
df <- html_table(html_data, fill = TRUE, convert = FALSE)[[1]]
df <- cbind(df, 
         list_rbind(lapply(strsplit(df$Release, ".", fixed = TRUE), 
                              (\(u) data.frame(major = as.integer(u[1]), 
                                               minor = as.integer(u[2])))))) |>
  filter(major > 1 | (major == 1 & minor > 7)) |>
mutate(Date = mdy(Date), packages = map2(major, minor, manifest)) -> z
  
# saveRDS(df, "~/Downloads/globalpackages.rds")
df <- readRDS("~/Downloads/globalpackages.rds")
z <- df |> unnest_longer(packages) |> 
  mutate(version = major * 100 + minor, category = packages$category, package = packages$package, .keep = "none")

# Are there any duplicate entries by category
# z |> group_by(category, package, version) |> summarize(N = n()) |> filter(N > 1)
# nrow is zero. All okay

# the packages that have switched versions
# z |> select(-version) |> distinct() |> group_by(package) |> summarize(N = n()) |> filter(N > 1) |> kable(format = 'pipe')

current_version <- max(z$version)
z |> 
  group_by(package) |>
  summarize(category = category[which.max(version)],
            first_version = min(version),
            last_version = max(version)) |>
  arrange(package) -> w

write.csv(w, outfile_location)
