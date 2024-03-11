# global_package_history.R
library(tidyverse)
library(glue)
library(rvest)
library(xml2)
library(curl)
library(yaml)
library(kableExtra)
# TODO CLeanup and operationalize

# create a data frame consisting of release, biocViews category, package for all history
# the package version are from http://bioconductor.org/config.yaml, element r_ver_for_bioc_ver

outfile_location <- "conversion/manifest_to_packages_table.csv"

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

file_path <- 'http://bioconductor.org/config.yaml'
bioc_ver <- yaml.load_file(file_path)
bioc_ver <- data.frame(Release = names(bioc_ver$r_ver_for_bioc_ver))
df <- cbind(bioc_ver, 
         list_rbind(lapply(strsplit(bioc_ver$Release, ".", fixed = TRUE), 
                              (\(u) data.frame(major = as.integer(u[1]), 
                                               minor = as.integer(u[2])))))) |>
  filter(major > 1 | (major == 1 & minor > 7)) |>
  mutate(packages = map2(major, minor, manifest))


z <- df |> unnest_longer(packages) |> 
  mutate(version = major * 100 + minor, category = packages$category, package = packages$package, .keep = "none")

# Are there any duplicate entries by category
z |> group_by(category, package, version) |> summarize(N = n()) |> filter(N > 1)
# nrow is zero. All okay

# the packages that have switched versions
z |> select(-version) |> distinct() |> group_by(package) |> summarize(N = n()) |> filter(N > 1) |> kable(format = 'pipe')

current_version <- max(z$version)
z |> 
  group_by(package) |>
  summarize(category = category[which.max(version)],
            first_version = min(version),
            last_version = max(version)) |>
  arrange(package) -> w

write.csv(w, outfile_location, quote=FALSE, row.names = FALSE)
