import cv2


# 寻找第一个上边缘，即黑色像素点个数大于阈值的行
def find_first_edge_index(row_pixel_nums, pixel_threshold):
    for i in range(len(row_pixel_nums)):
        if row_pixel_nums[i] > pixel_threshold:
            return i
    return -1


# 判断在第一个上边缘之上是否存在若干含有少量黑色像素点的行(即"NEW"图标的上半部分)
def is_new_gacha_above_edge(row_pixel_nums, edge_index, pixel_threshold, num_threshold):
    return len([i for i in row_pixel_nums[0:edge_index] if 0 < i < pixel_threshold]) > num_threshold


# 判断整数列表中是否存在连续的required_amount个0，如果有，则返回连续0初始位置的index
def find_continuous_zeros(nlist, required_amount):
    i = 0
    while i < len(nlist):
        continuous_zeros_count = 0
        for j in range(len(nlist)-i):
            if nlist[i+j] == 0:
                continuous_zeros_count += 1
            else:
                break
            if continuous_zeros_count >= required_amount:
                return i
        i += continuous_zeros_count + 1
    return -1


# 判断十连抽得到的10张新卡组成的2*5方阵的两个上边缘之上的空白处有没有少量黑色像素点(即"NEW"图标的上半部分)
def is_new_gacha(row_pixel_nums):
    max_row_pixel = max(row_pixel_nums)
    first_edge_index = find_first_edge_index(row_pixel_nums, max_row_pixel * 0.5)
    if is_new_gacha_above_edge(row_pixel_nums, first_edge_index, max_row_pixel * 0.1, 5):
        return True
    residual_row_pixel_nums = row_pixel_nums[first_edge_index:]
    residual_row_pixel_nums = residual_row_pixel_nums[find_continuous_zeros(residual_row_pixel_nums, 5):]
    second_edge_index = find_first_edge_index(residual_row_pixel_nums, max_row_pixel * 0.5)
    return is_new_gacha_above_edge(residual_row_pixel_nums, second_edge_index, max_row_pixel * 0.1, 5)


def check_new_gacha(gacha_screenshot_path):
    try:
        # 读取图片并二值化
        image = cv2.imread(gacha_screenshot_path)
        img_gray = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2GRAY)
        image_binary = cv2.threshold(img_gray, 200, 255, cv2.THRESH_BINARY)[1]
        contours = cv2.findContours(image_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        # 寻找最大矩形轮廓
        max_area = 0
        for c in contours:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            if len(approx) == 4:
                if cv2.contourArea(c) > max_area:
                    max_area = cv2.contourArea(c)
                    max_approx = approx
        x = [max_approx[0][0][0], max_approx[1][0][0], max_approx[2][0][0], max_approx[3][0][0]]
        y = [max_approx[0][0][1], max_approx[1][0][1], max_approx[2][0][1], max_approx[3][0][1]]
        x.sort()
        y.sort()
        xlow = max(x[0], x[1])
        xhigh = min(x[2], x[3])
        ylow = max(y[0], y[1])
        yhigh = min(y[2], y[3])
        # 裁剪原图，得到主要部分
        image_cropped = image[ylow:yhigh, xlow:xhigh]
        # 对主要部分进行Otsu二值化滤去背景
        img_gray = cv2.cvtColor(image_cropped, cv2.COLOR_BGR2GRAY)
        img_Otsu = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        image_binary = cv2.threshold(img_Otsu, 60, 255, cv2.THRESH_BINARY_INV)[1]
        # 统计各行黑色像素点个数，并判断是否存在"NEW"
        row_pixel_nums = []
        for i in range(image_binary.shape[0]):
            row_pixel_nums.append(int(sum(image_binary[i, :]) / 255))
        return is_new_gacha(row_pixel_nums), False
    except:
        return False, True
