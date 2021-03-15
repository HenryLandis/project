import geoplot as gplt
import geoplot.crs as gcrs
import geopandas as gpd

## url: shorturl.at/byDH8
# use the 'naturalearth_lowers' geopandas datasets
world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowers'))

# rename the columns 
world.columns=['continent', 'name', 'CODE', 'geometry']

# merge with your species occurrence data by the same "country code?" or any parameter that is available in both the world and GBIF dataframe
df = pd.read_csv(data)
merge = pd.merge(world, df, on = 'X') 

merge.plot(column = '', scheme = '', figsize =(,), legend = True, cmap = '')
plt.show()

### kdeplot
# link: geopandas.org/gallery/plotting_with_geoplot.html
# under the kdeplot

ax = gplt.polyplot(world, projection=gcrs.AlbersEqualArea())
ax = gplt.kdeplot(df, cmap='Reds', shade=True, shade_lowest=True, clip=world) 
