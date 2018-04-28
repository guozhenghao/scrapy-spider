- Linux和windows上编码不一样，注释里注明方法
- 需要解决的问题已解决，原来需要进行的数据清洗操作已不用进行
- ........................................................................

- 爬虫执行完毕后，需要清楚数据库中 place 为空的地点
    - [示例网页](http://www.yb21.cn/post/code/065201.html),最后一个元素为空但是标签
    - 直接清洗数据库数据即可，再次爬取时可以修改爬虫。本次由于已经爬了两小时了，不再修改
    - 清洗数据库命令: 切换到相关数据库下，执行: `db.getCollection('zipCode').remove({"place":""})`
- 部分地区地址最终页数据有以下三种异常情况，需要处理(已处理)
    - 城内所有街道及单位
    - 全县各乡镇(N全县各乡镇#)
    - 其余各乡镇(N其余各乡镇#)
    
- `db.getCollection('zipCode').find({"place":{"$regex":"各乡镇|所有街道"}})`
- 查询异常数据
````
db.getCollection('zipCode').aggregate([
    { $match : { place : { $regex:"各乡镇|所有街道" } } },
    {$group: {_id: "$place", num_tutorial: {$sum: 1
            }
        }
    },
    { $match : { num_tutorial : { $gt:0 } } },
])
````
