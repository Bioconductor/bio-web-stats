# global_package_history.R
library(tidyverse)
library(glue)
library(rvest)
library(xml2)
library(curl)

# create a data frame consisting of release, biocViews category, package for all history
# the package version are from the admin/manifest Bioc project:
# git clone git@git.bioconductor.org:admin/manifest
# The description of the packages will be in 
# 
#  https://www.bioconductor.org/packages/3.15/data/annotation/src/contrib/PACKAGES


# Get the releases from https://bioconductor.org/about/release-announcements/ by web scraping

outfile_location <- "~/Downloads/manifest_to_packages_table.csv"
table_data_location <- "~/Downloads/packages_table-data.csv"

manifest_template <- "https://www.bioconductor.org/packages/{version}/{category}/src/contrib/PACKAGES"

manifest <- \( major, minor) {
  categories = c("bioc", "data/annotation", "data/experiment")
  if (major > 2 || (major == 2 && minor > 11))
  {
    
    categories <- append(categories, "workflows")
  }
  mapply(\(category, version) {
    con <- curl(glue(manifest_template))
    result <- read.dcf(con)
    close(con)
    result
    },
         categories, glue("{major}.{minor}"))
}

file_path <- "conversion/bioc_versions.html"
html_data <- read_html(file_path)
df <- html_table(html_data, fill = TRUE, convert = FALSE)[[1]]
x <- cbind(df, 
           Reduce(rbind, lapply(strsplit(df$Release, ".", fixed = TRUE), 
                                (\(u) data.frame(major=u[1], minor=u[2]))))) |>
  filter(major > 1 | (major = 1 & minor > 7)) |> 
  mutate(Date = mdy(Date), packages = map2(major, minor, manifest))



for (i in 1:nrow(df)) {
  print(df$Release[i])
  x <- manifest(df$Release[i], "workflows")
}

version <- x$Release[1]
category <- "bioc"
uri <- glue(manifest_template)
con <- curl(uri)
y <- read.dcf(glue(manifest_template))


result <- Reduce(rbind, mapply((\(u, version_id) {
    system(glue("git checkout {u}"))
    files = dir(pattern = "*.txt")
    names(files) <- sapply(strsplit(files, ".", fixed = TRUE), (\(u) u[1]))
    Reduce(rbind,mapply((\(v, category) {
       x <- readLines(v)
       packages <- sapply(x[startsWith(x, "Package:")], (\(z) {
          trimws(strsplit(z, "Package:")[[1]][2])
         }), USE.NAMES = FALSE)
       data.frame(version=version_id, category=category, package=packages)
    }), files, sapply(strsplit(files, ".", fixed = TRUE), (\(u) u[1])), SIMPLIFY = FALSE))
  }), 
    branch_list,
    sapply(strsplit(branch_list, "_"), 
           (\(u) paste0("v", as.character(as.numeric(u[2])*100+as.numeric(u[3])), collapse = ""))),
    SIMPLIFY = FALSE
))

# write.csv(result, "manifest_matrix.csv")
result <- read.csv("/Users/rshear/Downloads/manifest_matrix.csv")

p_c <- unique(result[,c("package", "category")])
x <-split(p_c$category, p_c$package)

# Packages in 2 or more categories
multi_cat <- x[which(sapply(split(p_c$category, p_c$package), length) > 1)]
length(multi_cat)
# packages in software testing
swt_pac <- p_c[p_c$category == "software-testing", "package"]
table(p_c[p_c$package %in% swt_pac,])

# ignore the (software, software-testing) pairs
i <- sapply(multi_cat, (\(u) !identical(sort(u),c( "software","software-testing"))))
multi_cat2 <- multi_cat[i]

r3 <- result[result$package %in% names(multi_cat2),]
r3s <- split(r3, r3$package)
for (i in r3s) {
  print(glue("\n{i$package[1]}\n"))
  x <- split(i, i$category)
  for (j in x) {
    r <- range(j$version)
    print(glue("\t{j$category[1]}\t{r[1]}-{r[2]}"))
  }
}


# Here is the generation of the database table
table_data <- Reduce(rbind, lapply(split(result, result$package), (\(i) {
  u <- i[order(i$version),]
  first <- u$version[1]
  last <- u$version[nrow(u)]
  if (last == "v318") {
    last <- ""
  }
  data.frame(category=u$category[1], package=u$package[1], first, last)
  }
)))
write.csv(table_data, table_data_location, col.names = FALSE)
