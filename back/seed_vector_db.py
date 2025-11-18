"""
向量数据库种子脚本
向向量数据库添加示例文档
"""
from llama_index.core import Document
from app.rag.rag_service import update_knowledge_base
from app.utils.logger import logger


def seed_vector_database():
    """添加示例文档到向量数据库"""
    try:
        logger.info("开始添加向量数据库数据...")
        
        # 示例文档数据（产品知识库）
        documents = [
            Document(
                text="""
                智能手表 Pro 产品说明
                
                产品名称：智能手表 Pro
                价格：1299.00 元
                
                功能特点：
                1. 健康监测：24小时心率监测、血氧检测、睡眠分析
                2. 运动模式：支持50+种运动模式，GPS定位
                3. 智能通知：来电提醒、消息推送、日程提醒
                4. 续航能力：正常使用7天，省电模式14天
                5. 防水等级：IP68，支持游泳监测
                
                适用人群：
                - 运动爱好者
                - 健康关注者
                - 商务人士
                
                常见问题：
                Q: 如何充电？
                A: 使用磁吸充电器，约2小时充满。
                
                Q: 支持哪些手机？
                A: 支持 iOS 12+ 和 Android 8+ 系统。
                
                Q: 保修期多久？
                A: 整机保修1年，电池保修6个月。
                """,
                metadata={
                    "source": "产品手册",
                    "category": "智能手表",
                    "product": "智能手表 Pro"
                }
            ),
            Document(
                text="""
                无线耳机 Air 产品说明
                
                产品名称：无线耳机 Air
                价格：599.00 元
                
                功能特点：
                1. 音质：采用10mm动圈单元，支持AAC编码
                2. 降噪：主动降噪技术，降噪深度达35dB
                3. 续航：单次使用6小时，配合充电盒30小时
                4. 连接：蓝牙5.2，支持快速配对
                5. 防水：IPX4防水等级，适合运动使用
                
                适用场景：
                - 日常通勤
                - 运动健身
                - 办公学习
                
                常见问题：
                Q: 如何配对？
                A: 打开充电盒，长按配对键3秒，在手机蓝牙设置中搜索连接。
                
                Q: 降噪效果如何？
                A: 可有效降低环境噪音，适合在嘈杂环境中使用。
                
                Q: 充电需要多久？
                A: 耳机充电约1小时，充电盒充电约2小时。
                """,
                metadata={
                    "source": "产品手册",
                    "category": "音频设备",
                    "product": "无线耳机 Air"
                }
            ),
            Document(
                text="""
                智能音箱 Mini 产品说明
                
                产品名称：智能音箱 Mini
                价格：299.00 元
                
                功能特点：
                1. 语音助手：内置AI语音助手，支持语音控制
                2. 音质：360度环绕音效，2.5英寸全频单元
                3. 智能家居：支持控制1000+智能设备
                4. 内容：支持音乐、新闻、天气、闹钟等功能
                5. 连接：WiFi、蓝牙双模式
                
                适用场景：
                - 家庭娱乐
                - 智能家居控制
                - 语音助手
                
                常见问题：
                Q: 如何设置？
                A: 下载官方APP，按照提示连接WiFi并完成设置。
                
                Q: 支持哪些音乐平台？
                A: 支持QQ音乐、网易云音乐、喜马拉雅等主流平台。
                
                Q: 可以控制哪些智能设备？
                A: 支持智能灯、空调、电视、窗帘等常见智能家居设备。
                """,
                metadata={
                    "source": "产品手册",
                    "category": "智能家居",
                    "product": "智能音箱 Mini"
                }
            ),
            Document(
                text="""
                售后服务政策
                
                退换货政策：
                1. 7天无理由退货：商品未使用，包装完好
                2. 15天换货：质量问题或非人为损坏
                3. 1年保修：整机质量问题免费维修
                
                配送说明：
                1. 全国包邮（偏远地区除外）
                2. 一般地区2-3天送达
                3. 支持货到付款
                
                联系方式：
                客服电话：400-123-4567
                客服邮箱：service@example.com
                在线客服：工作日 9:00-21:00
                
                常见问题：
                Q: 如何申请退货？
                A: 在订单页面点击"申请退货"，填写原因并提交。
                
                Q: 运费谁承担？
                A: 质量问题由商家承担，无理由退货由买家承担。
                
                Q: 维修需要多久？
                A: 一般3-7个工作日，具体时间以实际情况为准。
                """,
                metadata={
                    "source": "售后服务",
                    "category": "政策说明"
                }
            ),
            Document(
                text="""
                订单查询和物流跟踪
                
                如何查询订单：
                1. 登录账号，进入"我的订单"
                2. 输入订单号查询
                3. 联系客服查询
                
                订单状态说明：
                - 待付款：订单已创建，等待支付
                - 处理中：订单已支付，正在准备发货
                - 已发货：商品已发出，可查看物流信息
                - 已完成：订单已完成，可申请售后
                - 已取消：订单已取消
                
                物流跟踪：
                1. 在订单详情页查看物流信息
                2. 点击物流单号查看详细轨迹
                3. 支持快递100、菜鸟裹裹等平台查询
                
                常见问题：
                Q: 订单什么时候发货？
                A: 一般付款后24小时内发货，预售商品按页面说明时间发货。
                
                Q: 如何修改收货地址？
                A: 发货前可在订单页面修改，发货后需联系客服。
                
                Q: 可以加急配送吗？
                A: 部分商品支持加急配送，具体以商品页面说明为准。
                """,
                metadata={
                    "source": "订单服务",
                    "category": "使用指南"
                }
            ),
            Document(
                text="""
                支付方式说明
                
                支持的支付方式：
                1. 支付宝：支持余额、花呗、信用卡
                2. 微信支付：支持余额、零钱、信用卡
                3. 银行卡：支持各大银行储蓄卡和信用卡
                4. 货到付款：部分商品支持
                
                支付安全：
                1. 所有支付均通过第三方安全平台
                2. 不存储任何支付密码信息
                3. 支持支付密码和指纹验证
                
                常见问题：
                Q: 支付失败怎么办？
                A: 检查账户余额、网络连接，或更换支付方式。
                
                Q: 支持分期付款吗？
                A: 部分商品支持花呗、信用卡分期，具体以支付页面显示为准。
                
                Q: 退款多久到账？
                A: 一般3-7个工作日，具体时间以银行处理为准。
                """,
                metadata={
                    "source": "支付服务",
                    "category": "使用指南"
                }
            )
        ]
        
        logger.info(f"准备添加 {len(documents)} 个文档到向量数据库...")
        logger.info("注意：这可能需要几分钟时间，请耐心等待...")
        
        # 更新知识库（带重试机制）
        max_retries = 3
        success = False
        
        for attempt in range(max_retries):
            try:
                logger.info(f"尝试添加文档（第 {attempt + 1}/{max_retries} 次）...")
                success = update_knowledge_base(documents)
                
                if success:
                    break
                else:
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 10
                        logger.warning(f"添加失败，{wait_time} 秒后重试...")
                        import time
                        time.sleep(wait_time)
                    else:
                        logger.error("所有重试均失败")
                        
            except Exception as e:
                logger.error(f"尝试 {attempt + 1} 失败: {str(e)}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 10
                    logger.warning(f"{wait_time} 秒后重试...")
                    import time
                    time.sleep(wait_time)
        
        if success:
            logger.info("✅ 向量数据库数据添加成功！")
            logger.info(f"   - 成功添加: {len(documents)} 个文档")
            return True
        else:
            logger.error("❌ 向量数据库数据添加失败")
            logger.error("可能的原因：")
            logger.error("  1. 网络连接问题（请检查网络或使用代理）")
            logger.error("  2. GEMINI_API_KEY 无效或配额不足")
            logger.error("  3. API 服务暂时不可用")
            logger.error("\n建议：")
            logger.error("  - 检查网络连接")
            logger.error("  - 验证 GEMINI_API_KEY 是否正确")
            logger.error("  - 稍后重试")
            return False
            
    except Exception as e:
        logger.error(f"添加向量数据库数据失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    seed_vector_database()

