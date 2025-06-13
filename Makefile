TARGETS=aptera_data coupon_round extract_coupon_investments priority_delivery_sanitizer

all: $(TARGETS)	

aptera_data: any
	ln -f $^ $@

coupon_round: any
	ln -f $^ $@

extract_coupon_investments: any
	ln -f $^ $@

priority_delivery_sanitizer: any
	ln -f $^ $@

# cat is needed because otherwise zip seeks to beginning of file and
# overwrites the #! string
any:	*.py
	rm -f any; (echo '#!/usr/bin/python3'; zip - $^) | cat > $@ && chmod +x $@

clean:
	rm -f $(TARGETS) any *~

.PHONY:	clean all
